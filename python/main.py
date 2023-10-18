import shutil
import argparse

import theme
import sticker


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="bilibili-vocaloid-stickers toolset", prog="pdm start")
    parser_command = parser.add_subparsers(dest="command", help="command to execute", required=True)

    parser_command_sticker               = parser_command.add_parser("sticker", help="sticker related actions")
    parser_command_sticker_action        = parser_command_sticker.add_subparsers(dest="action", help="sticker command to execute", required=True)
    parser_command_sticker_action_fetch  = parser_command_sticker_action.add_parser("fetch", help="fetch the LIST of stickers")
    parser_command_sticker_action_dump   = parser_command_sticker_action.add_parser("dump", help="dump (download) a specific sticker")
    parser_command_sticker_action_dump.add_argument("id", type=int, help="the sticker id to dump (download)")
    parser_command_sticker_action_find  = parser_command_sticker_action.add_parser("find", help="find a specific sticker in LOCAL CACHE")
    parser_command_sticker_action_find.add_argument("keyword", type=str, help="the string to find")
    parser_command_sticker_action_show   = parser_command_sticker_action.add_parser("show", help="show a specific sticker that have already downloaded")
    parser_command_sticker_action_show.add_argument("id", type=int, help="the sticker id to show")
    parser_command_sticker_action_pack   = parser_command_sticker_action.add_parser("pack", help="pack ALL stickers that have already downloaded")
    parser_command_sticker_action_pack.add_argument("-s", "--silent", action="store_true", help="do not print the filename when packing")
    parser_command_sticker_action_pack.add_argument("-g", "--readme", action="store_true", help="generate README.md when packing")
    parser_command_sticker_action_upload = parser_command_sticker_action.add_parser("upload", help="upload ALL stickers to Tencent COS")
    parser_command_sticker_action_upload.add_argument("--dry", action="store_true", help="do not upload, just print the filename")
    parser_command_sticker_action_resize = parser_command_sticker_action.add_parser("resize", help="resize ALL stickers for Telegram")
    parser_command_sticker_action_resize.add_argument("target", type=str, choices=["tg"], help="the target to resize for")
    parser_command_sticker_action_readme = parser_command_sticker_action.add_parser("update-readme", help="update README.md")
    parser_command_sticker_action_readme.add_argument("--tg", action="store_true", help="update Telegram links in README.md")

    parser_command_theme                 = parser_command.add_parser("theme", help="theme related actions")
    parser_command_theme_action          = parser_command_theme.add_subparsers(dest="action", help="theme command to execute", required=True)
    parser_command_theme_action_dump     = parser_command_theme_action.add_parser("dump", help="dump (download) a specific theme")
    parser_command_theme_action_dump.add_argument("id", type=int, help="the theme id to dump (download)")
    parser_command_theme_action_gif      = parser_command_theme_action.add_parser("svga", help="start a tool for SVGA conversion")
    parser_command_theme_action_gif.add_argument("--port", type=int, default=8080, help="the port to listen")
    parser_command_theme_action_gif.add_argument("--host", type=str, default="127.0.0.1", help="the host to listen")
    parser_command_theme_action_open     = parser_command_theme_action.add_parser("open", help="open a specific theme that have already downloaded")
    parser_command_theme_action_open.add_argument("id", type=int, help="the theme id to open")
    parser_command_theme_action_list     = parser_command_theme_action.add_parser("list", help="list all themes that have already downloaded")

    parser_command_clean                 = parser_command.add_parser("clean", help="clean the dist folder")

    arguments = parser.parse_args()
    if arguments.command == "clean":
        shutil.rmtree("dist", ignore_errors=True)
    if arguments.command == "sticker":
        sticker.main(arguments)
    if arguments.command == "theme":
        theme.main(arguments)
