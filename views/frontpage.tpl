<html>
<head>
    <link href="/static/main.css" rel="stylesheet" type="text/css">
</head>
<body onLoad="document.urlpost.url.focus();document.urlpost.url.value=document.urlpost.url.value">
    %include topbar title="3d3.ca Short URLs and Pastebin", url="http://3d3.ca/", rurl=None, passwd=None
    <div class="separate">shorten a url</div>
    <div class="submiturl">
        <form name="urlpost" method="POST"><table class="urltable"><tr>
        <td class="longtd">Shorten URL<br /><input class="longinput" type="text" name="url" value="http://"></td>
            <td>Password<br /><input type="password" name="p"></td>
            <td><br /><input type="submit" name="button" value="Shorten"></td>
        </tr></table></form>
    </div><br />
    <div class="separate">or submit a paste</div>
    <div class="submitpaste">
        <form method="POST"><table class="pastetable">
            <tr>
                <td class="longtd">Paste Title<br /><input class="longinput" type="text" name="title"></td>
                <td>Highlight As<br /><input type="text" name="format"></td>
                <td>Password<br /><input type="password" name="p"></td>
                <td><br /><input type="submit" name="button" value="Paste"></td>
            </tr>
            <tr>
                <td colspan="4" class="longtd">Paste Contents<br /><textarea class="pastetext" name="paste"></textarea></tr>
            </tr>
        </table></form>
    </div>
</body>
</html>
