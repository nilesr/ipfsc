# The problem

Imagine I, Bob have a file, cat.png, and I want to send it to my friend, Alice. I would run something like `ipfs add -q cat.png | mail alice@example.com`. 

Alice recieves the message, and does one of several things. If she has ipfs installed, she can do `ipfs get (the hash)`. If not, she may do `wget https://ipfs.io/ipfs/(the hash)`. After she has aquired the the file, she may wish to view it, at which point she will have to run `file (the hash)` to determine it's MIME type, then rename it to something friendly, like kitten.png, and open it in her favourite image viewer.

The original name of the file, cat.png, has been lost. In this context, it's not a real issue, but what if Bob and Alice's mutual friend Joe wants cat.png. He either has to know the cryptographic hash of the file, or send an email to Bob or Alice requesting the file. If he contacts Bob, he may get an answer the next time Bob checks his email, which may not be very often. If he emails Alice, on the other hand, Alice doesn't know what Joe is talking about, the only file she recieved from Bob was kitten.png.

# Solutions considered

IPFS as it stands acts as a distributed hash table, linking  
    Hash of the file -> Hash of the public key of a node that has the file.

One possibility to resolve this problem is a second distributed hash table, essentially duct taped on top of IPFS. To access cat.png, a client would have to parse through two tables:  
    String filename -> Hash of the file
    Hash of the file -> Hash of the public key of a node that has the file.

There are a few problems with this, first and foremost, if a IPFSC node propegates a message through the secondary distributed hash table saying that cat.png points to a file that was uploaded by a different node that does not use IPFSC, then the first host goes down, that data can easily be lost. The solution to this would be to have individual nodes cache large chunks of the filesystem's namespace, which is infesable and could drive users away from IPFSC. 

Another problem is that filenames would be immutable. If one person registers cat.png, nobody else can register that name without having conflicting data between different nodes in the distributed hash table. A possible solution would be an update system, where nodes are free to register cat.png as many times as they like, and each time they must also propegate the date and time at which they registered it. Nodes trying to access cat.png would only accept the most recent date. This would allow any node to overwrite the filename of any other node, as well as forcing nodes to keep out-of-date data on hand in case the node that registered the same filename at a newer date goes down.

Another possibility is a centralized server, with immutable filenames. Each time a node registers a new filename, they must register the new node with the centralized server. This would require a high-availability and perfectly synced database, preferabley a galera cluster. It would also be very expensive and not entire solve the problem of immutability. 

# IPFSC

Enter IPFSC, or Inter Planetary File System Clusters. It works much like the second solution, but with mutable filenames, fine grained permission control, synchronicity and security.

The system works like this. It is assumed that you have a group of roughly 3-50 friends with which you want to share data. One friend hosts a server, and each friend sends a copy of their key to that server, along with a human-friendly username like `alice` or `joe`. These user creation requests are then confirmed by the server owner or an appointed administrator. Each friend's IPFSC client connects to this server whenever you mount IPFSC, and gets information about filenames over the network. When you type a command from your console like `cat /path/to/mnt/cat.png`, IPFSC seamlessly creates a request message for "/cat.png", signs it with the user's key, and sends it to the server. The server makes sure that this user has read access to /cat.png, and if so, finds the hash of the requested file, signs it again and sends it back. IPFSC then passes on the request to IPFS which downloads the file using the file's cryptographic hash, then returns it to the application. This works with directories as well, if a user does `ipfs add -r some_directory`, or more realistically, `cp -R some_directory /math/to/mnt/`, they will be able to run `cd /path/to/mnt/some_directory; ls` and see all of the files in their directory and access them seamlessly.

The system defaults to only allowing contact from servers in it's database, but you can configure it to allow public read access or even public write access. Individual users can be automatically allocated home folders with friendly usernames, and can give users and groups read and write access to files or directories, using both unix-like chmod and fsetacl, which are stored in the server's database

Users with write access to a file cannot actually modify the file, all they can do is change the stored cryptographic hash of the file, which has the same apparent effect, but the original file will remain pinned on the original user's IPFS daemon. Support for automatic unpinning is planned as a long-term goal.
