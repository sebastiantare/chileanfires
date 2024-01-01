# Set DEV in the script
DEV=true

if [ "$DEV" ]; then
    echo 'export API_SRC="$HOME/Development/chileanfires"' >> ~/.bashrc
    echo 'export CONDA_SRC="$HOME/anaconda3"' >> ~/.bashrc
else
    echo 'export API_SRC="/root"' >> ~/.bashrc
    echo 'export CONDA_SRC="/root/miniconda3"' >> ~/.bashrc
fi

# Display the exported variables
echo "Env variables set to:"
echo "Development=$DEV"
echo "API_SRC=$API_SRC"
echo "CONDA_SRC=$CONDA_SRC"
echo ""

# Source the modified ~/.bashrc to apply the changes immediately
source ~/.bashrc
