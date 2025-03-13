import subprocess
import os
import dotenv
import pexpect

def sakura_cloud_ubuntu_connect(private_key_path, config_host):
    """
    SSHエージェントを起動し、.envからパスフレーズを取得して秘密鍵を登録、SSH接続を試みる。

    Args:
        private_key_path (str): 秘密鍵のパス。
        config_host (str): ~/.ssh/config で定義されたホスト名。
    """

    try:
        # .env ファイルの読み込み
        dotenv.load_dotenv()
        passphrase = os.getenv("SAKURA_CLOUD_UBUNTU_PASS")

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
    private_key_path = os.path.expanduser('~/.ssh/odoo-sk-mrt.pem')  # 秘密鍵のパス
    config_host = "sakura-cloud-ubuntu" # ~/.ssh/config で定義されたホスト名

    sakura_cloud_ubuntu_connect(private_key_path, config_host)