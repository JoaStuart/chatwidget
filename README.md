# Twitch Chat Widget

This project is a chat combo widget for twitch, inspired by the one [**@Charborg**](https://twitch.tv/charborg) uses.

As the name suggests, this widget highlights when chat sends similar or identical messages multiple times. It helps streamers quickly grasp the overall vibe of their chat, making it easier to read at a glance and also is a funny addition for viewers.

The widget tracks chat messages in real-time and supports emotes from Twitch as well as popular third-party services like BetterTTV, FFZ, and SevenTV.

## How to run

### 0. Prequisites

- [**Python 3.12**](https://www.python.org/downloads) or higher must be installed for this application to work.
- [**Git**](https://git-scm.com/downloads) is recommended for cloning the repository, but it is not strictly needed.
- [**OBS**](https://obsproject.com/download) is also required, but you most likely already have this installed.

### 1. Cloning the repo

```bash
git clone https://github.com/JoaStuart/chatwidget.git
```

<sub>If you don't have Git installed, you can also download the ZIP archive of this repo and un-zip it manually</sub>

### 2. Installing libraries

Open a CMD or Terminal inside the cloned directory and type the following commands:

```bash
pip install -r requirements.py
```

### 3. Running the application

```bash
cd src
python main.py
```

<sub>Depending on your system, you might need to switch out the `python` or `pip` commands with the command your OS uses, like `python3.12` or `python -m pip`</sub>

### 4. Adding the Dashboard to OBS

In your OBS in the top menu bar go to `Docks` > `Custom Browser Docks...`.

In the ...

- ... `Dock Name` field, enter `ChatWidget`,
- ... `URL` field, enter `http://localhost:4150/dashboard`,

... press `Apply` and close the window. You can move this new dock where ever you want. Here you can change config values - this will be important later.

### 5. Adding the Widget

In the scene you want the widget, add a new `Browser` source, name it and press `OK`.

In the `URL` field, enter `http://localhost:4150/widget` and press `OK` to close the config window.

### 6. Configuring and connecting to Twitch

In the configuration dashboard we created earlier, you can now enter your name inside the `Broadcaster` field, the other values are not important for now.

For the application to be able to read messages in your name, you now need to connect your Twitch account by clicking on `Connect` at the top and authorizing the application.

Now message combos from your chat should automatically appear inside the widget. Third party emotes from [BetterTTV](https://betterttv.com), [SevenTV](https://betterttv.com) and [FrankerFaceZ](https://www.frankerfacez.com) are also automatically loaded.

## Reading a different chat

Reading the chat of a different streamer than the account you connected the application with is also supported, but a little more config setup is needed.

In the Configuration Dashboard ...

- ... tick the Checkbox next to `Reading user`, ...
- ... enter the name of the account you connected the application with in the field to the right and ...
- ... enter the name of the streamer whose chat to display into the field next to `Broadcaster`.

Again, changes should be visible within seconds.

## Nerd talk

### Implementation

The widget is written in Python, leveraging the built-in `http.server` module to serve the widget as a browser source. This choice keeps the implementation lightweight and avoids the overhead of more advanced frameworks.

For the frontend, plain HTML, CSS, and JavaScript are used to render the widget. This ensures faster rendering in OBS compared to frameworks that rely on heavy JavaScript rendering.

The widget integrates with the Twitch API to retrieve chat messages and emotes, while also supporting popular third-party emote services like BetterTTV, SevenTV, and FFZ through their respective APIs.

To ensure quick communication between the backend and frontend, the widget runs locally. A prebuilt version is provided for ease of use.

Customization is made simple through a configuration UI, available as an OBS dock. This allows users to adjust settings easily without leaving their streaming software.

### Future plans

- Adding support for YouTube chat
- TTS when message gets spammed
- More fine control using config
- Rewrite as an OBS plugin for ease of access???
