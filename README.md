# Twitch Chat Widget

[![Python 3.12+](https://img.shields.io/badge/Python-3.12%2B-blue?logo=python)](https://www.python.org/)
![License](https://img.shields.io/github/license/JoaStuart/chatwidget)
![Last Commit](https://img.shields.io/github/last-commit/JoaStuart/chatwidget)
[![OBS Studio](https://img.shields.io/badge/OBS_Studio-supported-green?logo=obsstudio)](https://obsproject.net/)
[![Twitch API](https://img.shields.io/badge/Twitch-API-%239146FF?logo=twitch)](https://dev.twtich.tv/)

This project is a chat combo widget for twitch, inspired by the one [**@Charborg**](https://twitch.tv/charborg) uses.

As the name suggests, this widget highlights when chat sends similar or identical messages multiple times. It helps streamers quickly grasp the overall vibe of their chat, making it easier to read at a glance and also is a funny addition for viewers.

The widget tracks chat messages in real-time and supports emotes from Twitch as well as popular third-party services like BetterTTV, FFZ, and SevenTV.

## How to Run

### 0. Prerequisites

- [**OBS Studio**](https://obsproject.com/download) (you likely already have this installed).

### 1. Download and Launch the Application

1. Go to the [**Releases**](https://github.com/JoaStuart/chatwidget/releases) section of the repository.
2. Download the latest release for your operating system.
3. Run the downloaded file.

### 2. Add the Dashboard to OBS

1. In OBS, go to **Docks** > **Custom Browser Docks...**.
2. Enter the following:
   - **Dock Name**: `ChatWidget`
   - **URL**: `http://localhost:4150/dashboard`
3. Click **Apply** and close the window.
4. Position the dock as needed. This dashboard allows you to configure the widget.

### 3. Add the Widget to OBS

1. In the desired scene, add a **Browser** source.
2. Enter the following in the **URL** field:  
   `http://localhost:4150/widget`
3. Click **OK** to close the configuration window.

### 4. Configure and Connect to Twitch

1. Open the configuration dashboard in OBS.
2. Enter your Twitch username in the **Broadcaster** field (other fields can be left as is for now).
3. Click **Connect** at the top and authorize the application to access your Twitch account.

Once connected, chat combos will appear in the widget automatically. Third-party emotes from **BetterTTV**, **SevenTV**, and **FrankerFaceZ** will also load automatically.

### Optional: Displaying Another Streamer’s Chat

If you want to show chat messages from a streamer other than the account you're connected with:

1. Open the **Configuration Dashboard** in OBS.
2. Enable the **Reading user** checkbox.
3. Enter:
   - Your connected Twitch username in the **Reading user** field.
   - The name of the streamer whose chat you want to display in the **Broadcaster** field.

Changes should take effect within seconds.

## Building / Running from source

### 0. Prerequisites for building / running

- [**Python 3.12**](https://www.python.org/downloads) or higher.
- [**Git**](https://git-scm.com/downloads) (optional, for cloning the repository).
- [**Make**](https://www.gnu.org/software/make/).
- [**OBS Studio**](https://obsproject.com/download) (you likely already have this installed).

### 1. Clone the Repository

Using Git (recommended):

```bash
git clone https://github.com/JoaStuart/chatwidget.git
```

Without Git:

- Download the ZIP file from the repository page and extract it.

### 2. Install Dependencies

Navigate to the project folder in CMD or Terminal:

```bash
pip install -r requirements.txt
```

<sub>_Note: Replace `pip` with `python -m pip` or `pip3` depending on your system._</sub>

### 3.1. Running the application

Run the following command:

```bash
make run
```

### 3.2. Building the application

Run the following command:

```bash
make build
```

The generated binary will be located inside the `dist` directory.

### 4. Setting up

For setup, start the application and continue with [adding the Dashboard to OBS](#2-add-the-dashboard-to-obs).

## Implementation

The widget is written in Python, leveraging the built-in `http.server` module to serve the widget as a browser source. This choice keeps the implementation lightweight and avoids the overhead of more advanced frameworks.

For the frontend, plain HTML, CSS, and JavaScript are used to render the widget. This ensures faster rendering in OBS compared to frameworks that rely on heavy JavaScript rendering.

The widget integrates with the Twitch API to retrieve chat messages and emotes, while also supporting popular third-party emote services like BetterTTV, SevenTV, and FFZ through their respective APIs.

To ensure quick communication between the backend and frontend, the widget runs locally. A prebuilt version is provided for ease of use.

Customization is made simple through a configuration UI, available as an OBS dock. This allows users to adjust settings easily without leaving their streaming software.

## Acknowledgments

This project was inspired by the chat combo widget used by [**@Charborg**](https://twitch.tv/charborg).

Special thanks to the following services and APIs for making this project possible:

- [**Twitch API**](https://dev.twitch.tv): For providing access to chat messages and emotes.
- [**BetterTTV (BTTV)**](https://betterttv.com): For third-party emote support.
- [**SevenTV (7TV)**](https://7tv.app): For extended emote libraries.
- [**FrankerFaceZ (FFZ)**](https://www.frankerfacez.com): For additional emotes and chat customization options.

Thank you to the OBS community for making streaming tools easy to integrate and configure!

## Future plans

- Adding support for YouTube chat
- TTS when message gets spammed
- More fine control using config
- Rewrite as an OBS plugin for ease of access???
