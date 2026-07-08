import pkg from "chai";
const { expect } = pkg;
import hre from "hardhat";
import { time } from "@nomicfoundation/hardhat-network-helpers";

describe("HealthAccessControl Integration Tests", function () {
  let contract;
  let owner;
  let patient;
  let provider;
  let otherAccount;
  let recordHash;
  const PENDING_DURATION = 60; // 60 seconds

  beforeEach(async function () {
    [owner, patient, provider, otherAccount] = await hre.ethers.getSigners();
    const HealthAccessControl = await hre.ethers.getContractFactory("HealthAccessControl");
    contract = await HealthAccessControl.deploy();
    await contract.waitForDeployment();

    // Use a mock 32-byte hash
    recordHash = hre.ethers.keccak256(hre.ethers.toUtf8Bytes("MRI_Brain_Scan_2026"));

    // Register a record first for testing access grants
    await contract.connect(patient).registerRecord(
      recordHash,
      "MRI Brain Scan",
      "Metro Neurology Center",
      Math.floor(Date.now() / 1000)
    );
  });

  describe("Record Registration", function () {
    it("should register a record with correct fields", async function () {
      const record = await contract.getRecord(patient.address, recordHash);
      expect(record.exists).to.be.true;
      expect(record.recordType).to.equal("MRI Brain Scan");
      expect(record.facility).to.equal("Metro Neurology Center");
    });

    it("should reject double registration of the same record", async function () {
      await expect(
        contract.connect(patient).registerRecord(
          recordHash,
          "MRI Brain Scan",
          "Metro Neurology Center",
          Math.floor(Date.now() / 1000)
        )
      ).to.be.revertedWith("HealthAccessControl: record already exists");
    });
  });

  describe("Access Grant Flow: Grant -> Time-lock -> Confirm -> Revoke", function () {
    it("should execute the full lifecycle correctly", async function () {
      const expiration = Math.floor(Date.now() / 1000) + 3600; // 1 hour from now

      // 1. Initiate Grant (enters pending state)
      await expect(
        contract.connect(patient).initiateGrant(
          provider.address,
          recordHash,
          1, // VIEW_ONLY
          expiration
        )
      ).to.emit(contract, "GrantAccessInitiated");

      // Verify it's pending
      let [pending, pendingUntil] = await contract.isPending(patient.address, provider.address, recordHash);
      expect(pending).to.be.true;
      expect(pendingUntil).to.be.greaterThan(0);

      // Verify no access yet
      let [hasAccess, accessLevel] = await contract.checkAccess(patient.address, provider.address, recordHash);
      expect(hasAccess).to.be.false;

      // 2. Confirm Grant before lock expires (should fail)
      await expect(
        contract.connect(patient).confirmGrant(provider.address, recordHash)
      ).to.be.revertedWith("HealthAccessControl: still in pending period");

      // Fast-forward time by 60 seconds
      await time.increase(PENDING_DURATION);

      // 3. Confirm Grant after lock expires (should succeed)
      await expect(
        contract.connect(patient).confirmGrant(provider.address, recordHash)
      ).to.emit(contract, "GrantAccessConfirmed");

      // Verify active access
      [pending, pendingUntil] = await contract.isPending(patient.address, provider.address, recordHash);
      expect(pending).to.be.false;

      [hasAccess, accessLevel] = await contract.checkAccess(patient.address, provider.address, recordHash);
      expect(hasAccess).to.be.true;
      expect(accessLevel).to.equal(1);

      // 4. Revoke Access immediately (should succeed)
      await expect(
        contract.connect(patient).revokeAccess(provider.address, recordHash)
      ).to.emit(contract, "RevokeAccess");

      // Verify access is gone
      [hasAccess, accessLevel] = await contract.checkAccess(patient.address, provider.address, recordHash);
      expect(hasAccess).to.be.false;
    });
  });

  describe("Access Grant Cancellation", function () {
    it("should allow patient to cancel a pending grant", async function () {
      const expiration = 0; // no expiry

      // Initiate
      await contract.connect(patient).initiateGrant(
        provider.address,
        recordHash,
        1,
        expiration
      );

      // Cancel before the 60 seconds is up
      await expect(
        contract.connect(patient).cancelPendingGrant(provider.address, recordHash)
      ).to.emit(contract, "GrantAccessCancelled");

      // Verify it is no longer pending and not active
      const [pending] = await contract.isPending(patient.address, provider.address, recordHash);
      expect(pending).to.be.false;

      const [hasAccess] = await contract.checkAccess(patient.address, provider.address, recordHash);
      expect(hasAccess).to.be.false;
    });

    it("should not allow cancellation after confirmation period has been confirmed", async function () {
      await contract.connect(patient).initiateGrant(
        provider.address,
        recordHash,
        1,
        0
      );
      await time.increase(PENDING_DURATION);
      await contract.connect(patient).confirmGrant(provider.address, recordHash);

      await expect(
        contract.connect(patient).cancelPendingGrant(provider.address, recordHash)
      ).to.be.revertedWith("HealthAccessControl: cannot cancel an active grant");
    });
  });

  describe("Access Guards and Modifiers", function () {
    it("should enforce onlyPatient modifier on initiateGrant", async function () {
      // otherAccount attempts to initiate grant for patient's record
      await expect(
        contract.connect(otherAccount).initiateGrant(
          provider.address,
          recordHash,
          1,
          0
        )
      ).to.be.revertedWith("HealthAccessControl: record does not exist");
    });

    it("should enforce onlyPatient modifier on confirmGrant", async function () {
      await contract.connect(patient).initiateGrant(
        provider.address,
        recordHash,
        1,
        0
      );
      await time.increase(PENDING_DURATION);

      // otherAccount attempts to confirm
      await expect(
        contract.connect(otherAccount).confirmGrant(provider.address, recordHash)
      ).to.be.revertedWith("HealthAccessControl: record does not exist");
    });

    it("should enforce onlyPatient modifier on cancelPendingGrant", async function () {
      await contract.connect(patient).initiateGrant(
        provider.address,
        recordHash,
        1,
        0
      );

      // otherAccount attempts to cancel
      await expect(
        contract.connect(otherAccount).cancelPendingGrant(provider.address, recordHash)
      ).to.be.revertedWith("HealthAccessControl: record does not exist");
    });

    it("should enforce onlyPatient modifier on revokeAccess", async function () {
      await contract.connect(patient).initiateGrant(
        provider.address,
        recordHash,
        1,
        0
      );
      await time.increase(PENDING_DURATION);
      await contract.connect(patient).confirmGrant(provider.address, recordHash);

      // otherAccount attempts to revoke
      await expect(
        contract.connect(otherAccount).revokeAccess(provider.address, recordHash)
      ).to.be.revertedWith("HealthAccessControl: record does not exist");
    });
  });
});
