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

        # 1. SSHエージェントの起動と環境変数の設定
        try:
            process = subprocess.Popen(['ssh-agent', '-s'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()

            if stderr:
                print(f"ssh-agent エラー: {stderr.decode().strip()}")
                raise Exception("ssh-agent failed")

            if process.returncode != 0:
                print(f"ssh-agent failed with exit code {process.returncode}")
                raise Exception(f"ssh-agent failed with exit code {process.returncode}")

            output = stdout.decode().strip()
            for line in output.splitlines():
                if "SSH_AUTH_SOCK=" in line:
                    os.environ["SSH_AUTH_SOCK"] = line.split("=")[1].split(";")[0] # exportを取り除く
                elif "SSH_AGENT_PID=" in line:
                    os.environ["SSH_AGENT_PID"] = line.split("=")[1].split(";")[0] # exportを取り除く

            # print(os.environ) # 環境変数の確認を追加

        except FileNotFoundError:
            print("ssh-agentが見つかりません。インストールされているか確認してください。")
            raise
        except Exception as e:
            print(f"ssh-agent起動中にエラーが発生しました: {e}")
            raise

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
            print(e.stderr.decode())
    except FileNotFoundError:
        print(f"ファイルが見つかりません。{private_key_path} を確認してください")
    except ValueError as e:
        print(f"エラーが発生しました: {e}")
    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    ssh_connect()