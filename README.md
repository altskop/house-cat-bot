# Onyx Bot Alpha

OnyxBot is a discord bot written in Python for my personal use. 
It uses the [discord.py](https://github.com/Rapptz/discord.py/tree/rewrite) library written by Rapptz.
The bot should be relatively easy to reconfigure and reprogram should you want to have one for yourself.

## Core Features:
- The bot is able to monitor discord messages (in either public channels it's connected to, and DM channels), parse them, compare them to pre-written models, and generate new responses.

At this point there are no other functioning features.

## Planned Core Features
- TTS in voice channels
- Larger sets of message and response models to increase the impact of the bot
- TBD

This list will be updated once I figure out what I want this bot to do. I haven't really given it a thought and just rolled with everything I could think of.

## Project Structure
Currently there are three main modules in the project:
- [onyx.py](onyx.py) : this file determines behaviour of OnyxBot. It is responsible for setting it up and managing its during runtime. It will require a "config" file in the directory to run (see "config.example" for details)
- [response_builder.py](response_builder.py) : this package contains the logic for reading and generating responses. The message models are defined in [locale/messages.locale](locale/messages.locale), and the word dictionary is populated from [locale/dictionary.locale](locale/dictionary.locale) 
- [testing.py](testing.py) : this module is used to unit test the [response_builder.py](response_builder.py)

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

The project requires **Python 3.6** to run.

You will need to get the 1.0 version of [discord.py](https://github.com/Rapptz/discord.py/tree/rewrite) as a dependency:

```
pip install -U discord.py[voice]
```

If 0.16.12 version is being installed, run the following command instead:

```
pip install -U git+https://github.com/Rapptz/discord.py@rewrite#egg=discord.py[voice]
```

### Installing

To set up your development environment for this project, clone this repository first.

```
git clone https://github.com/altskop/OnyxBot.git
```

Open the folder as a project in PyCharm or any other IDE of your choice.

You should be all set to start developing and running the project.

## Running the tests

In order to run automated testing for the [response_builder.py](response_builder.py) (the module responsible for recognizing message patterns and generating replies), create your test cases in [testing.py](testing.py).

Some test cases are already present in package. An example below demonstrates how to create a test case:

```
test.unit_test_fits_template("INSULT", "u r good", False)
``` 

Where `test` is a reference to **UnitTester** class, `unit_test_fits_template` is a method of **UnitTester** that tests `msg_fits_template` method of **ResponseBuilder**, `"INSULT"` is a message model tag to compare input to, `"u r good"` is the input, and `False` is the expected output of the method.

If the input string matches the message model, the method will return `True`. Otherwise, it will return `False`. For more information on this, examine the documentation in [response_builder.py](response_builder.py).

Example output after running the [testing.py](testing.py):

```---------------------------------------------
TOTAL TESTS RAN: 17
PASSED: 17  |  FAILED: 0
```

## Deployment

Will add support for containerization some time in the future. 

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Thank you Rapptz for the awesome library
* Thank you Discord Team for the continuous API support and development
