import subprocess
import os
import dotenv
import pexpect

def ssh_connect():
    """
    SSHエージェントを起動し、.envからパスフレーズを取得して秘密鍵を登録、SSH接続を試みる。
    """

    try:
        # .env ファイルの読み込み
        dotenv.load_dotenv()
        # 秘密鍵のパス
        private_key_path = os.path.expanduser(os.getenv("PRIVATE_KEY_PATH"))
        # ~/.ssh/config で定義されたホスト名
        config_host = os.getenv("CONFIG_HOST")
        # 秘密鍵のパスフレーズ
        passphrase = os.getenv("SAKURA_CLOUD_UBUNTU_PASS")

        if private_key_path is None:
            raise ValueError(".envファイルにPRIVATE_KEY_PATHが設定されていません。")
        if config_host is None:
            raise ValueError(".envファイルにCONFIG_HOSTが設定されていません。")
        if passphrase is None:
            raise ValueError(".envファイルにSAKURA_CLOUD_UBUNTU_PASSが設定されていません。")

        # 1. SSHエージェントの起動
        subprocess.run(['eval', '$(ssh-agent -s)'], shell=True, check=True)

        # 2. 秘密鍵の登録
        child = pexpect.spawn(f'ssh-add {private_key_path}')
        child.expect('Enter passphrase for')  # パスフレーズ入力プロンプトを待機
        child.sendline(passphrase)
        child.expect(pexpect.EOF)  # 終了を待機

        if child.exitstatus != 0:
            print(f"ssh-add エラー: {child.before.decode().strip()}")  # エラーメッセージを表示
            raise Exception(f"ssh-add failed with exit code {child.exitstatus}")

        # 4. SSH接続
        subprocess.run(['ssh', config_host], check=True)

    except subprocess.CalledProcessError as e:
        print(f"エラーが発生しました: {e}")
        if hasattr(e, "stderr"):
            print(e.stderr)
    except FileNotFoundError:
        print(f"ファイルが見つかりません。{private_key_path} を確認してください")
    except ValueError as e:
        print(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    ssh_connect()