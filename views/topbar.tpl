<div class="topbar">
    <table class="tbtable">
        <tr>
            <td class="l"><a href="http://3d3.ca/">3d3</a></td>
            <td class="m">{{title}}</td>
            <td class="r"><a href="{{url}}">{{url}}</a> \\
            % if rurl and passwd:
                <a href="{{rurl}}?p={{passwd}}">(raw)</a>\\
            % elif rurl:
                <a href="{{rurl}}">(raw)</a>\\
            % end
            </td></tr>
    </table>
    <div class="spacing"/>
</div>
