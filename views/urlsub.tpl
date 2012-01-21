<html>
<head>
    <link href="/static/main.css" rel="stylesheet" type="text/css">
</head>
<body>
    %include topbar title="URL Submission Successful", url=url, rurl=rurl, passwd=None
    <div class="authbox" style="background-color:#FFF; width:60%">
        The URL<br />
        <div class="url">{{source}}</div>
        has successfully been shortened to<br />
        <a class="url" href="{{url}}">{{url}}</a>
    </div>
</body>
</html> 
