import subprocess
import os
import sys

def activate_venv_and_run_script(script_path):
    """
    カレントディレクトリの .venv をアクティベートし、指定された Python スクリプトを実行する。

    Args:
        script_path (str): 実行する Python スクリプトのパス。
    """

    venv_path = os.path.join(os.getcwd(), ".venv", "bin", "activate")
    if not os.path.exists(venv_path):
        print(".venv がカレントディレクトリに存在しません。")
        return

    try:
        # .venv をアクティベートし、スクリプトを実行
        process = subprocess.Popen(
            ["bash", "-c", f"source {venv_path} && python3 {script_path}"],
            stdout=sys.stdout,
            stderr=sys.stderr,
            shell=False #bash -c　を使うのでTrueにはできない
        )
        process.communicate()

        if process.returncode != 0:
            print(f"スクリプトの実行に失敗しました。終了コード: {process.returncode}")

    except FileNotFoundError:
        print(f"スクリプトが見つかりません: {script_path}")
    except Exception as e:
        print(f"予期しないエラーが発生しました: {e}")

if __name__ == "__main__":
    script_path = "sakura_cloud_ubuntu_connect.py"  # 実行するスクリプトの名前

    activate_venv_and_run_script(script_path)