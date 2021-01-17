from glob import glob

from setuptools import setup

package_name = 'rqt_robot_dashboard'
setup(
    name=package_name,
    version='0.5.8',
    package_dir={'': 'src'},
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name + '/images', glob('images/*.svg')),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    author="Ze'ev Klapow",
    maintainer='Aaron Blasdel',
    maintainer_email='ablasdel@gmail.com',
    description=(
        'rqt_robot_dashboard provides an infrastructure for building robot dashboard plugins in rqt.'
    ),
    license='BSD',
)
