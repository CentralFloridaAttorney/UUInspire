### Setting Up a Conda Environment for Unity ML-Agents

This tutorial will guide you through setting up a Conda environment for training ML agents using Unity ML-Agents Toolkit. We'll cover creating the environment, installing the necessary packages, and resolving any common issues that may arise during the setup.

#### Step 1: Install Conda
If you don't have Conda installed, download and install Anaconda from [here](https://www.anaconda.com/products/distribution).

#### Step 2: Create a Conda Environment
Open your terminal and create a new Conda environment named `mlagents_env`. You can name the environment anything you like, but for this tutorial, we'll use `mlagents_env`.

```bash
conda create --name mlagents_env python=3.9
```

#### Step 3: Activate the Conda Environment
Activate your newly created environment.

```bash
conda activate mlagents_env
```

#### Step 4: Install Required Packages
Install the required packages including ML-Agents and TensorBoard.

```bash
pip install pyyaml
pip install mlagents
pip install tensorboard
```

#### Step 5: Fix Potential Protobuf Version Issue
If you encounter an issue with Protobuf, you may need to downgrade it. This is a common issue with ML-Agents due to compatibility with certain Protobuf versions.

```bash
pip install protobuf==3.20.0
```

#### Step 6: Verify Installation
Verify that the ML-Agents CLI tool is installed correctly by running:

```bash
mlagents-learn -h
```

You should see the usage instructions for `mlagents-learn`.

### Common Issues and Troubleshooting

1. **Command not found**: If `mlagents-learn` is not found, ensure that your Conda environment is activated and the package is installed correctly.

    ```bash
    conda activate mlagents_env
    pip install mlagents
    ```

2. **Protobuf errors**: If you encounter errors related to Protobuf, downgrade to version 3.20.0 as shown in Step 5.

3. **Missing packages**: If any packages are missing or not found, ensure your Conda environment is active and you have the correct package names. Use `pip install <package_name>` to install any missing packages.

### Example Setup Commands

Here’s a summary of the commands used in the tutorial for quick reference:

```bash
# Create and activate Conda environment
conda create --name mlagents_env python=3.9
conda activate mlagents_env

# Install required packages
pip install pyyaml
pip install mlagents
pip install tensorboard

# Downgrade Protobuf if necessary
pip install protobuf==3.20.0

# Verify installation
mlagents-learn -h
```

By following these steps, you should have a fully functional Conda environment for training ML agents using the Unity ML-Agents Toolkit. If you encounter any issues, refer to the troubleshooting section or consult the official [ML-Agents documentation](https://docs.unity3d.com/Packages/com.unity.ml-agents@2.0/manual/index.html).

