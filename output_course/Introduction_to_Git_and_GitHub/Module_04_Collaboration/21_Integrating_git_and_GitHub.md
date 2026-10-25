# 📖 Integrating git and GitHub

Git is a disconnected client/server application. This means that repositories are kept on a server and copied to your local machine. Some Git operations, like git push or git pull, will synchronize your copy with the remote repository.

While some organizations run their own private Git servers, most rely on a hosted solution. By far, the most popular is GitHub, but GitLab and Bitbucket are also in use. The Git command line can work with any of these.

## Integrating Git and GitHub

You can use either HTTPS or SSH with the command-line Git client to interact with GitHub. If you are pushing a commit, or working with a private repository, you will need to authenticate. Authentication methods differ depending on whether you’re using HTTPS or SSH.

We’ll demonstrate several ways of using Git with your GitHub account.

## HTTPS authentication

### Command-line with HTTPS

Install the Git CLI according to your operating system. When you push to a GitHub repository over HTTPS, or clone a private repository, Git will prompt you for your GitHub username and password.

If you don’t want to enter your username and password every time, you can store them in a file called .netrc in your home directory, like this: 

`machine GitHub.com login my-username password my-password machine api.GitHub.com login my-username password my-password`

Make sure the file is not readable by anyone else, or Git may ignore it.

### Command-line HTTPS with token

Instead of storing your password in plaintext in the .netrc file, you can generate a personal access token and use that in place of your password. See [Managing your personal access tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens).

### Git Credential Manager

Git Credential Manager (GCM) is a tool that securely stores your passwords and supplies them to Git without your intervention. It works on Linux, macOS, and Windows, and it supports multi-factor authentication too. You can read more about it [here](https://github.com/git-ecosystem/git-credential-manager).

## SSH authentication

In the previous module, you learned how to generate an SSH key pair and use it for logging in to remote hosts. You can use the same SSH key to authenticate with GitHub.

To add your SSH key for use with GitHub:

  1. Find the public key you generated in the previous module. It will have a filename like id_rsa.pub.

  2. Open [GitHub.com](https://github.com/) in your browser.

  3. Click on your profile icon in the top right corner and select **Settings**.

  4. Go to **SSH and GPG keys**.

  5. Click **New SSH key**.

  6. Paste the contents of your public key into the text box and click **Add SSH key**.




## Key takeaways

Integrating Git and GitHub is necessary for storing, sharing, and publishing your code. Git is responsible for everything GitHub-related that happens locally on your computer. GitHub is a cloud-based service that can store, share, and publish your code. Git and GitHub need to be able to communicate with each other. 
