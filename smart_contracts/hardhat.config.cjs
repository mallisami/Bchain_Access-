const path = require("path");
require("@nomicfoundation/hardhat-toolbox");
require("dotenv/config");

subtask("compile:solidity:solc:get-build", async (args, hre, runSuper) => {
  if (args.solcVersion === "0.8.26") {
    return {
      compilerPath: require.resolve("solc/soljson.js"),
      isSolcJs: true,
      version: args.solcVersion,
      longVersion: "0.8.26+commit.8a97fa7a",
    };
  }
  return runSuper();
});

module.exports = {
  solidity: {
    version: "0.8.26",
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
      blockGasLimit: 30000000,
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
  },
  gasReporter: {
    enabled: process.env.REPORT_GAS === "true",
    blockGasLimit: 30000000,
  },
};
