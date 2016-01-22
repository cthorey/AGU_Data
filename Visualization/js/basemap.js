
var name = 'test'
var dataurl  = 'https://raw.githubusercontent.com/cthorey/agu_data/master/Notebook/'+name+'.json'

var map = new Datamap({
    element: document.getElementById('container'),
    height : 900,
    
    fills: {
        Potential : 'red',
        LOW: '#123456',
        MEDIUM: 'blue',
        UNKNOWN: 'rgb(0,0,0)',
        defaultFill: '#afafaf'
    },
    
    dataType : 'json',
    dataUrl : dataurl,
    geographyConfig: {
        popupTemplate: function(geography, data) {
            return ['<div class="hoverinfo">' + geography.properties.name,
                    '<br/>Number of potential collaborators :' + data.Num_collab,
                    data.Names,
                    '<\div>'].join('')
        },
        highlightBorderWidth: 3
    }
});

d3.select('#update').on('click', function(e) {
    var dataurl = ''
    map.updateChoropleth(data);
});;
