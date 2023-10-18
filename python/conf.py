import os
import toml

class Configuration:
    def __init__(self) -> None:
        self.SHELL_OPEN_MACOSX     = "open"
        self.SHELL_OPEN_WINDOWS    = "explorer"
        self.SHELL_OPEN_LINUX      = "xdg-open"
        self.PATH_NFTS             = "assets/nfts"
        self.PATH_THEMES           = "assets/themes"
        self.PATH_THEMES_GIF       = "assets/themes_gif"
        self.PATH_STICKERS         = "assets/stickers"
        self.PATH_STICKERS_LIST    = "assets/stickers.tsv"
        self.PATH_STICKERS_TG_LINK = "assets/telegram.ini"
        self.PATH_README           = "README.md"
        self.PATH_TEMPLATE_SVGA    = "svga/template.html"
        self.PATH_SVGA_LIBRARY     = "svga/svga.min.js"
        self.PATH_SVGA_RSEOURCES   = "_resources"
        self.CRED_BILIBILI_COOKIES = "secrets/bilibili.com_cookies.txt"
        self.CRED_COS_CREDENTIALS  = "secrets/cos.toml"
        self.DIST_STICKERS         = "dist/stickers"
        self.DIST_TELEGRAM         = "dist/stickers_telegram"
        self.DIST_SVGA_WWWROOT     = "dist/svga/wwwroot"
        self.URL_FETCH_STICKERS    = "https://api.bilibili.com/x/emote/setting/panel?business=reply"
        self.URL_DUMP_STICKERS_F   = "https://api.bilibili.com/x/emote/package?business=reply&ids={}"
        self.URL_DUMP_THEME_F      = "https://api.bilibili.com/x/garb/v2/mall/suit/detail?from=&from_id=&item_id={}&part=suit"
        self.COS_SECRET_ID         = None
        self.COS_SECRET_KEY        = None
        self.COS_REGION            = "ap-guangzhou"
        self.COS_BUCKET            = "luotianyi-dev-1251131545"
        self.COS_PREFIX            = "bilibili-vocaloid-stickers/"
        self.COS_DOMAIN            = "luotianyi-dev-1251131545.file.myqcloud.com"
        self.MARK_CDN              = "<!-- MARK OF AUTOGEN COS CDN LINKS -->"
        self.MARK_TELEGRAM         = "<!-- MARK OF AUTOGEN TELEGRAM LINKS -->"

        if os.path.exists(self.CRED_COS_CREDENTIALS):
            cos = toml.load(self.CRED_COS_CREDENTIALS)
            self.COS_SECRET_ID  = cos["secret-id"]
            self.COS_SECRET_KEY = cos["secret-key"]
            if cos.get("oversea-upload"):
                self.COS_REGION = "accelerate"
    
    def __str__(self) -> str:
        return "<Configuration: {}>".format(self.__dict__)

CONF = Configuration()
