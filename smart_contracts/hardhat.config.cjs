const path = require("path");
require("@nomicfoundation/hardhat-toolbox");
require("dotenv/config");

subtask("compile:solidity:solc:get-build", async (args, hre, runSuper) => {
  if (args.solcVersion === "0.8.19") {
    return {
      compilerPath: path.join(__dirname, "soljson-v0.8.19+commit.7dd6d404.js"),
      isSolcJs: true,
      version: args.solcVersion,
      longVersion: "0.8.19+commit.7dd6d404",
    };
  }
  return runSuper();
});

module.exports = {
  solidity: {
    version: "0.8.19",
    settings: {
      optimizer: {
        enabled: true,
        runs: 200
      }
    }
  },
  networks: {
    hardhat: {
      chainId: 1337,
    },
    localhost: {
      url: "http://127.0.0.1:8545",
      chainId: 1337,
    },
    sepolia: {
      url: process.env.SEPOLIA_RPC_URL || "",
      accounts: process.env.PRIVATE_KEY ? [process.env.PRIVATE_KEY] : [],
      chainId: 11155111,
    }
  }
};
