import setuptools

setuptools.setup(
    name='TwitchBot',
    author='Daenara',
    version='0.0.3',
    url='https://github.com/HumanDotExe/TwitchBot',
    packages=setuptools.find_packages(),
    py_modules=["chat_bot", "data_types", "twitch_api", "utils", "webserver"],
    python_requires='>=3.7, <3.9',
    install_requires=["twitchAPI", "twitchio", "PyYAML", "schema"],
    package_data={
        '': ['streams/default.yaml'],
    }
)