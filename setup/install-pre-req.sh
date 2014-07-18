cd ~/
echo "Updating apt-get cache!"
apt-get update
echo "Copying over interfaces file"
cp -f ./BlueTracker-Py/setup/interfaces /etc/network/interfaces
echo "Setup dbus"
cp -f ./BlueTracker-Py/setup/org.bluez.service /usr/local/share/dbus-1/system-services/org.bluez.service
echo "Get the required libraries to build bluez"
apt-get install -y libusb-dev libdbus-1-dev libglib2.0-dev libudev-dev libical-dev libreadline-dev python-dbus python-setuptools python-daemon python-gobject
echo "Getting bluez"
wget http://www.kernel.org/pub/linux/bluetooth/bluez-4.101.tar.xz
echo "Extracting bluez"
sudo unxz bluez-4.101.tar.xz
tar xvf bluez-4.101.tar
echo "Copying updated mgmtops.c"
cp -f ./BlueTracker-Py/setup/mgmtops.c ./bluez-4.101/plugins
echo "Getting latest projects..."
git clone https://github.com/rodtoll/BlueTracker-Py.git
git clone https://github.com/evilpete/ISYlib-python.git
cd ISYlib-python
python ./setup.py install
cd ..
echo "Configuring then building bluez"
cd bluez-4.101
echo "Configuring..."
./configure
echo "Building..."
make
echo "Installing..."
make install
cd ..
echo "Done!"
