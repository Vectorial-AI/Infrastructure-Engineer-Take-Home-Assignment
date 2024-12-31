# Clean up previous builds
Remove-Item -Path package -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path lambda_function.zip -Force -ErrorAction SilentlyContinue

# Create package directory
New-Item -ItemType Directory -Path package

# Clean pip cache
pip cache purge

# Install dependencies with specific versions
pip install --platform manylinux2014_x86_64 --implementation cp --python-version 3.12 --only-binary=:all: --target ./package -r requirements.txt --no-cache-dir

# Copy all Python files to the root of the package
Get-ChildItem -Filter "*.py" | Copy-Item -Destination package

# Create ZIP file
Compress-Archive -Path package\* -DestinationPath lambda_function.zip -Force

# Clean up
Remove-Item -Path package -Recurse -Force 