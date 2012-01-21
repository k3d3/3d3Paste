<html>
<head>
    <link href="/static/main.css" rel="stylesheet" type="text/css">
</head>
<body onLoad="document.pwbox.p.focus();">
    %include topbar title="Password Protected", url=url, rurl=None, passwd=None
    % if incorrect:
    <div class="authbox" style="background-color:#FDD">
        Password Incorrect.<br />
    % else:
    <div class="authbox" style="background-color:#FFF">
    % end
        Please enter the URL password
        <div class="bottom">
            <form name="pwbox" method="GET">
                <table>
                    <tr>
                        <td class="input"><input class="pwbox" type="password" name="p"></td>
                        <td align="right"><input type="submit" value="Continue"></td>
                    </tr>
                </table>
            </form>
        </div>
    % if incorrect:
    </div>
    % end
    </div>
</body>
</html>
