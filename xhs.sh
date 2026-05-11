#!/usr/bin/env bash

# 默认设置
ENGINE=${XHS_BROWSER_ENGINE:-"cloak"}

# 显示帮助
show_help() {
    echo "使用方法: ./xhs.sh [选项] <命令> [参数]"
    echo ""
    echo "选项:"
    echo "  -e, --engine ENGINE   指定底层引擎 (可选: camoufox, cloak, playwright)，默认: cloak"
    echo "  -p, --path PATH       如果引擎是 playwright，指定自定义防指纹浏览器内核二进制路径"
    echo "  -H, --humanize        开启拟人化操作 (针对 cloak 引擎，模拟真实鼠标轨迹和打字延迟)"
    echo "  -h, --help            显示此帮助信息"
    echo ""
    echo "支持的小红书 CLI 命令 (如 search, status, login, whoami 等):"
    echo "  ./xhs.sh search '测试'"
    echo "  ./xhs.sh -e cloak search '测试'"
    echo "  ./xhs.sh -e playwright -p /usr/local/bin/chrome status"
}

# 解析参数
HUMANIZE="0"
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -e|--engine) ENGINE="$2"; shift ;;
        -p|--path) EXECUTABLE_PATH="$2"; shift ;;
        -H|--humanize) HUMANIZE="1" ;;
        -h|--help) show_help; exit 0 ;;
        *) break ;; # 停止解析，剩余参数交给原始 CLI
    esac
    shift
done

# 如果没有命令传进来，显示帮助并执行原始的 --help
if [[ "$#" -eq 0 ]]; then
    show_help
    echo "----------------------------------------"
    uv run xhs --help
    exit 0
fi

# 设置环境变量
export XHS_BROWSER_ENGINE="$ENGINE"
export XHS_HUMANIZE="$HUMANIZE"
if [[ -n "$EXECUTABLE_PATH" ]]; then
    export XHS_BROWSER_EXECUTABLE="$EXECUTABLE_PATH"
fi

echo "🚀 [启动配置] 引擎: $XHS_BROWSER_ENGINE"
if [[ "$XHS_HUMANIZE" == "1" ]]; then
    echo "🤖 [启动配置] 拟人化模拟 (Humanize): 开启"
fi
if [[ -n "$XHS_BROWSER_EXECUTABLE" ]]; then
    echo "📍 [启动配置] 自定义内核路径: $XHS_BROWSER_EXECUTABLE"
fi
echo "----------------------------------------"

# 执行真正的 Python CLI
uv run xhs "$@"
