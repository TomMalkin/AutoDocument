# File Storages

File Storages are a way to standardise the load and save locations of your sources, templates and outcomes in AutoDocument. A File Storage is added by the Admin in the Advanced Section of the dashboard. So far the options are Posix filesystems, Windows filesystems, S3 Object Store and SharePoint Libraries.

## Windows Filesystem

You can map a remote Windows Filesystem like a Network Share to a local path in AutoDocument. For example, if your users use a common Drive denoting the share, say "N: Drive", then you can map that to a locally mounted path and then files can be referenced natively. "N:\ClientData" could be mapped locally to "/mnt/ClientData/", and then when defining a file, the Windows Share could be selected and the relative file "\Templates\InvoiceTemplate.docx" would work normally from the user's perspective.

(Note, Drive letters aren't used in the mount command - you must use the hostname or IP. Lets say N:\ is mapped to MyHost)

This requires a couple of steps.

1) The Windows drive is mounted on the host that is running the AutoDocument Container. For example:

`sudo mount -t nfs -o vers=4 MyHost:/ClientData /mnt/ClientData`

2) The mounted drive is set as a volume in the container, for example:

`docker run autodocument -p 4605:4605 -v /mnt/ClientData:/app/mnt/ClientData`

3) The Windows Share is now added to AutoDocument using the Add Windows FileSystem form in Advanced. Using the above setup, the Host and Remote Paths would be:

Host Path: /app/mnt/ClientData
Remote Path: N:\ClientData\

The users will be able to then use the N:\ClientData Windows Share when specifying files the , for example (N:\ClientData) -> (Templates\InvoiceTemplate.docx)

## Posix Filesystem

Posix File Systems work in much the same way. First mount the network share to the host, then use that mount as a volume in the container construction. Use the Add Posix file system form in Advanced to define the remote and host paths. Remember, the Remote Path is what the User will see when selecting that File Storage option.

## S3

AutoDocument can read and write from any S3 compatible storage option. Simply set the URL, username and password in the Advanced Form. When choosing that File Storage option, specify the Bucket and the file path within that bucket.

## SharePoint

SharePoint Libraries can also be used. The SharePoint "Site" url must be used, such as "https://mybusiness.sharepoint.com/sites/MySite/". Also specify the name of the Library within that Site. the Username and Password is the Microsoft username and password of the account that has enough permissions to read and write that SharePoint site. Note - Client Context isn't supported as it depends on when the SharePoint site was initialised (newer SharePoint sites won't allow app access without client certificates).

Specify the name of the file like any other once that File Storage option is selected, relative to the library, for example if the Library name is MyLibrary, then use "Templates/template.docx" (omitting the library).
