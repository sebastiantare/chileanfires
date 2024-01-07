# Set DEV in the script
DEV=false
API_SRC=""
CONDA_SRC=""

if [ "$DEV" = true ]; then
    API_SRC="$HOME/Development/chileanfires"
    CONDA_SRC="$HOME/anaconda3"
else
    API_SRC="/root"
    CONDA_SRC="/root/miniconda3"
fi

# Display the exported variables
echo "Env variables set to:"
echo "Development=$DEV"
echo "API_SRC=$API_SRC"
echo "CONDA_SRC=$CONDA_SRC"
echo ""

# Set the environment variables
echo "export API_SRC=$API_SRC" >> ~/.bashrc
echo "export CONDA_SRC=$CONDA_SRC" >> ~/.bashrc

# export DEV variable
echo "export DEV=$DEV" >> ~/.bashrc

# Source the modified ~/.bashrc to apply the changes immediately
source ~/.bashrc
