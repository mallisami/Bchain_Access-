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

      await expect(
        contract.connect(patient).confirmGrant(provider.address, recordHash)
      ).to.be.revertedWith("HealthAccessControl: no pending grant found");
    });

    it("should allow cancellation after the minimum wait when still unconfirmed", async function () {
      await contract.connect(patient).initiateGrant(provider.address, recordHash, 1, 0);
      await time.increase(PENDING_DURATION + 1);

      const [pending, earliestConfirmation] = await contract.isPending(
        patient.address,
        provider.address,
        recordHash
      );
      expect(pending).to.be.true;
      expect(earliestConfirmation).to.be.greaterThan(0);

      await expect(
        contract.connect(patient).cancelPendingGrant(provider.address, recordHash)
      ).to.emit(contract, "GrantAccessCancelled");

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

    it("should reject unsupported access levels", async function () {
      await expect(
        contract.connect(patient).initiateGrant(provider.address, recordHash, 2, 0)
      ).to.be.revertedWith("HealthAccessControl: only view access is supported");
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

  describe("Administrative Ownership", function () {
    it("should emit an event when ownership is transferred", async function () {
      await expect(contract.transferOwnership(otherAccount.address))
        .to.emit(contract, "OwnershipTransferred")
        .withArgs(owner.address, otherAccount.address);
      expect(await contract.owner()).to.equal(otherAccount.address);
    });

    it("should reject ownership transfer to the zero address", async function () {
      await expect(contract.transferOwnership(ethers.ZeroAddress))
        .to.be.revertedWith("HealthAccessControl: invalid new owner");
    });
  });

  describe("Post-Remediation Security & State Invariant Tests", function () {
    it("should reject confirming an already active grant", async function () {
      await contract.connect(patient).initiateGrant(provider.address, recordHash, 1, 0);
      await time.increase(PENDING_DURATION);
      await contract.connect(patient).confirmGrant(provider.address, recordHash);
      await expect(
        contract.connect(patient).confirmGrant(provider.address, recordHash)
      ).to.be.revertedWith("HealthAccessControl: grant is already active");
    });

    it("should return false from checkAccess after access has expired", async function () {
      const now = Math.floor(Date.now() / 1000);
      const expiration = now + 10; // expires in 10 seconds
      await contract.connect(patient).initiateGrant(provider.address, recordHash, 1, expiration);
      await time.increase(PENDING_DURATION);
      await contract.connect(patient).confirmGrant(provider.address, recordHash);

      // Fast-forward past expiration
      await time.increase(20);

      const [hasAccess, accessLevel] = await contract.checkAccess(patient.address, provider.address, recordHash);
      expect(hasAccess).to.be.false;
      expect(accessLevel).to.equal(0);
    });

    it("should reject initiating a grant with zero-address provider", async function () {
      await expect(
        contract.connect(patient).initiateGrant(ethers.ZeroAddress, recordHash, 1, 0)
      ).to.be.revertedWith("HealthAccessControl: invalid provider address");
    });

    it("should reject revoking access for a pending grant", async function () {
      await contract.connect(patient).initiateGrant(provider.address, recordHash, 1, 0);
      await expect(
        contract.connect(patient).revokeAccess(provider.address, recordHash)
      ).to.be.revertedWith("HealthAccessControl: grant is not active");
    });

    it("should allow initiating a new pending grant after revoking a previous one", async function () {
      await contract.connect(patient).initiateGrant(provider.address, recordHash, 1, 0);
      await time.increase(PENDING_DURATION);
      await contract.connect(patient).confirmGrant(provider.address, recordHash);
      await contract.connect(patient).revokeAccess(provider.address, recordHash);
      await expect(
        contract.connect(patient).initiateGrant(provider.address, recordHash, 1, 0)
      ).to.emit(contract, "GrantAccessInitiated");
    });
  });

  describe("Remediation Tests (Authorized Logger and Pause Policy)", function () {
    let gateway;

    beforeEach(async function () {
      [, , , gateway] = await hre.ethers.getSigners();
    });

    describe("Authorized Logger", function () {
      it("should allow owner to set authorized gateway", async function () {
        await expect(contract.connect(owner).setAuthorizedGateway(gateway.address))
          .to.emit(contract, "AuthorizedGatewayUpdated")
          .withArgs(ethers.ZeroAddress, gateway.address);
        expect(await contract.authorizedGateway()).to.equal(gateway.address);
      });

      it("should reject non-owner setting authorized gateway", async function () {
        await expect(
          contract.connect(otherAccount).setAuthorizedGateway(gateway.address)
        ).to.be.revertedWith("HealthAccessControl: caller is not the owner");
      });

      it("should reject setting authorized gateway to zero address", async function () {
        await expect(
          contract.connect(owner).setAuthorizedGateway(ethers.ZeroAddress)
        ).to.be.revertedWith("Invalid gateway");
      });

      it("should allow authorized gateway to log access attempt", async function () {
        await contract.connect(owner).setAuthorizedGateway(gateway.address);
        await expect(
          contract.connect(gateway).logAccessAttempt(
            patient.address,
            provider.address,
            recordHash,
            false,
            "failed attempt"
          )
        ).to.emit(contract, "AccessAttempt");
      });

      it("should allow owner to log access attempt", async function () {
        await expect(
          contract.connect(owner).logAccessAttempt(
            patient.address,
            provider.address,
            recordHash,
            false,
            "owner logging attempt"
          )
        ).to.emit(contract, "AccessAttempt");
      });

      it("should reject unauthorized address logging access attempt", async function () {
        await expect(
          contract.connect(otherAccount).logAccessAttempt(
            patient.address,
            provider.address,
            recordHash,
            false,
            "malicious log"
          )
        ).to.be.revertedWith("Unauthorized logger");
      });
    });

    describe("Pause Policy", function () {
      it("should allow owner to pause and unpause", async function () {
        expect(await contract.paused()).to.be.false;
        await contract.connect(owner).pause();
        expect(await contract.paused()).to.be.true;
        await contract.connect(owner).unpause();
        expect(await contract.paused()).to.be.false;
      });

      it("should reject non-owner pausing/unpausing", async function () {
        await expect(contract.connect(otherAccount).pause()).to.be.revertedWith(
          "HealthAccessControl: caller is not the owner"
        );
        await expect(contract.connect(otherAccount).unpause()).to.be.revertedWith(
          "HealthAccessControl: caller is not the owner"
        );
      });

      it("should enforce pause policy on grant actions", async function () {
        // Pause contract
        await contract.connect(owner).pause();

        // 1. initiateGrant should fail while paused
        await expect(
          contract.connect(patient).initiateGrant(provider.address, recordHash, 1, 0)
        ).to.be.revertedWith("HealthAccessControl: contract is paused");

        // Unpause to initiate a grant
        await contract.connect(owner).unpause();
        await contract.connect(patient).initiateGrant(provider.address, recordHash, 1, 0);

        // Pause again
        await contract.connect(owner).pause();

        // 2. confirmGrant should fail while paused
        await time.increase(PENDING_DURATION);
        await expect(
          contract.connect(patient).confirmGrant(provider.address, recordHash)
        ).to.be.revertedWith("HealthAccessControl: contract is paused");

        // 3. cancelPendingGrant should still work while paused (safety first)
        await expect(
          contract.connect(patient).cancelPendingGrant(provider.address, recordHash)
        ).to.emit(contract, "GrantAccessCancelled");

        // Initiate and confirm another grant for testing revocation while paused
        await contract.connect(owner).unpause();
        await contract.connect(patient).initiateGrant(provider.address, recordHash, 1, 0);
        await time.increase(PENDING_DURATION);
        await contract.connect(patient).confirmGrant(provider.address, recordHash);

        // Pause
        await contract.connect(owner).pause();

        // 4. revokeAccess should still work while paused (safety first)
        await expect(
          contract.connect(patient).revokeAccess(provider.address, recordHash)
        ).to.emit(contract, "RevokeAccess");
      });

      it("should resume all operations after unpause", async function () {
        await contract.connect(owner).pause();
        await contract.connect(owner).unpause();

        // Should successfully initiate and confirm
        await expect(
          contract.connect(patient).initiateGrant(provider.address, recordHash, 1, 0)
        ).to.emit(contract, "GrantAccessInitiated");

        await time.increase(PENDING_DURATION);

        await expect(
          contract.connect(patient).confirmGrant(provider.address, recordHash)
        ).to.emit(contract, "GrantAccessConfirmed");
      });
    });
  });
});
