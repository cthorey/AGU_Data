
var map = new Datamap({
    element: document.getElementById('container'),
    height : 900,
    
    fills: {
        HIGH: '#afafaf',
        LOW: '#123456',
        MEDIUM: 'blue',
        UNKNOWN: 'rgb(0,0,0)',
        defaultFill: '#afafaf'
    },
    
    data: {
        FRA: {
            fillKey: 'LOW',
            size : 2002,
            animal :' jaguar'
        },
        USA: {
            fillKey: 'MEDIUM',
            size : 10381,
            animal :' jaguar'
        }
    },

    geographyConfig: {
        popupTemplate: function(geography, data) {
            return ['<div class="hoverinfo">' + geography.properties.name,
                    '<br/>Electoral Votes :'+ data.size,
                    '<br/>Animal :'+ data.animal,
                    '<\div>'].join('')
        },
        highlightBorderWidth: 3
    }
});
