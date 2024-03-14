import requests
import os
from git import Repo
from datetime import datetime
import pytz

# GitHub API 相关信息
GITHUB_API_URL = "https://api.github.com/repos/aazooo/zjmf"
REPO_PATH = "zjmftb"  # 本地库路径

def check_update():
    # 发送GET请求获取最后更新时间
    headers = {}
    if 'GH_TOKEN' in os.environ:
        headers["Authorization"] = f"token {os.environ['GH_TOKEN']}"
    response = requests.get(GITHUB_API_URL, headers=headers)
    if response.status_code == 200:
        repo_info = response.json()
        last_updated_at = datetime.strptime(repo_info['updated_at'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=pytz.utc)
        
        # 检查本地库是否存在，如果不存在则克隆
        if not os.path.exists(REPO_PATH):
            Repo.clone_from(repo_info['clone_url'], REPO_PATH)
        
        # 打开本地库
        repo = Repo(REPO_PATH)
        
        # 获取本地库的最后提交时间并转换为UTC时间
        last_commit = repo.head.commit.committed_datetime.replace(tzinfo=pytz.utc)
        
        # 检查是否有更新
        if last_commit < last_updated_at:
            # 创建新分支并同步
            new_branch_name = f"update_{last_updated_at.strftime('%Y%m%d_%H%M%S')}"
            print(f"Creating new branch: {new_branch_name}")
            repo.git.checkout('-b', new_branch_name)
            print("Pulling changes from remote repository...")
            if 'GH_TOKEN' in os.environ:
                os.environ['GIT_ASKPASS'] = 'git_askpass.sh'
                with open('git_askpass.sh', 'w') as f:
                    f.write(f'echo "{os.environ["GH_TOKEN"]}"')
                repo.git.pull()
                os.remove('git_askpass.sh')
            else:
                repo.git.pull()
            repo.git.push('--set-upstream', 'origin', new_branch_name)
            print(f"Repository updated. New branch created: {new_branch_name}")
        else:
            print("Repository is up to date.")
    else:
        print("Failed to retrieve repository information.")

if __name__ == "__main__":
    check_update()
