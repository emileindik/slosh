# Slosh

For more information on using and configuring SSH through the SSH config file, check out this helpful guide: [Using the SSH Config File](https://linuxize.com/post/using-the-ssh-config-file/).


## Installation

```bash
$ pip install slosh
```

## Usage

By default `slosh` is simply a pass-through to the `ssh` command. So you can run any `ssh` command normally, using `slosh`.

```bash
$ slosh -i ~/.ssh/mykey.pem ubuntu@1.1.1.1 
```

#### Add new connection

To save a connection to the SSH config file add `--save-as <host alias>` to your connection command. The host alias is how you will reference the connection in the future. 
```bash
$ slosh -i ~/.ssh/mykey.pem --save-as myserver ubuntu@1.1.1.1 
```
In the above example we used `--save-as myserver` to save the connection information to the SSH config file under the alias `myserver`. This means that we can now run `slosh myserver` or `ssh myserver` to connect to the server.

#### Update connection

Simply use the --save-as option with the host alias of the connection you wish to update. Here we add compression (`-C`) and change the login username (`newuser`) of our original connection.

```bash
$ slosh -i ~/.ssh/mykey.pem -C --save-as myserver ubuntu@1.1.1.1 
```

### Supported options
The below `ssh` options are saved to the config. Let me know if you'd like more options to be added.

- `-l <user>`: Specifies the username for the connection.
- `-p <port>`: Specifies the port number for the connection.
- `-i <identity file>`: Specifies the path to the private key file for the connection.
- `-A`: Enables forwarding of the authentication agent connection.
- `-C`: Requests compression of all data.
- `-v`: Increases verbosity. Can be used up to three times (`-vvv`).

For a comprehensive list of all `ssh` options and their explanations, you can refer to the official SSH manual page: [SSH Manual Page](https://man7.org/linux/man-pages/man1/ssh.1.html).
