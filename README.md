# House Cat Bot

![python3.6](https://img.shields.io/badge/python-3.6-blue.svg) ![mit](https://img.shields.io/github/license/mashape/apistatus.svg)

House Cat is a multifunctional discord bot written in Python. 
It utilizes the [discord.py](https://github.com/Rapptz/discord.py/tree/rewrite) library written by Rapptz.

To add the bot to your server, please press [HERE](https://discordapp.com/api/oauth2/authorize?client_id=303023298743238656&permissions=36817984&scope=bot).

## Features:
- Meme Generation
- Games (Rock-Paper-Scissors, Cards Against Humanity)
- Polls
- Dice rolls
- Magic 8-Ball
- Thesaurization of a message

## Planned Core Features
- Allow bot to listen to voice (perhaps respond in some ways or record?). It could be controlled in voice to call Rhythm for example
- Soundboard functionality
- Add a fully-functional web dashboard

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

The project requires **Python 3.6** to run.

You will need to get the 1.0 version of [discord.py](https://github.com/Rapptz/discord.py/tree/rewrite) as a dependency:

```
pip install -U "discord.py[voice]"
```

If 0.16.12 version is being installed, run the following command instead:

```
pip install -U git+https://github.com/Rapptz/discord.py@rewrite#egg=discord.py[voice]
```

## Deployment

Populate the `storage` folder with data that the bot will need access to (such as fonts, databases, meme templates etc.). Create a docker volume first using `make storage` in the root directory of the project. The volume will act as persistent storage for the bot. Deleting the volume will result in data loss. **Keep in mind that running the command again will remove the existing volume.**

To build a docker image of House Cat bot, navigate to `house_cat` directory and run `make build`. You may also use `make run` to run the image after it was created, or `make start` to run it in detached mode.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Thanks to Rapptz for the awesome library
* Thanks to Discord Team for the continuous API support and development
