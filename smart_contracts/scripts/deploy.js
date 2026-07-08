import hre from "hardhat";
import fs from "fs";

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  console.log("Deploying with account:", deployer.address);

  const HealthAccessControl = await hre.ethers.getContractFactory("HealthAccessControl");
  const contract = await HealthAccessControl.deploy();

  await contract.waitForDeployment();

  const address = await contract.getAddress();
  console.log("HealthAccessControl deployed to:", address);
  console.log("Transaction hash:", contract.deploymentTransaction().hash);

  // Save deployment info
  const deploymentInfo = {
    contract: "HealthAccessControl",
    address: address,
    deployer: deployer.address,
    network: hre.network.name,
    chainId: hre.network.config.chainId,
    timestamp: new Date().toISOString(),
  };
  fs.writeFileSync("deployment.json", JSON.stringify(deploymentInfo, null, 2));
  console.log("Deployment info saved to deployment.json");
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
