/* IMPORT LIBRARIES */
const D3Node = require('d3-node')
const fs  = require('fs')
var Canvas = require('canvas')
var cloud = require('d3-cloud')
var http = require('http')
var mongoose = require('mongoose')


/* SET UP VARIABLES */
const options = { selector: '#container', container: '<div id="container"></div>' }
const d3n = new D3Node(options)
const d3 = d3n.d3

const dir = './output/'
const format = '.svg'
var colors = ['#29578f','#24b57a','#ffa500']
var numColors = colors.length


var svg = d3.select(d3n.document.querySelector('#container'))
			.append('svg')
			.attr('xmlns','http://www.w3.org/2000/svg')
            .attr('xmlns:xlink', 'http://www.w3.org/1999/xlink')
			.attr('width', 1100)
			.attr('height', 350)
			.append('g')
d3n.html()   // output: <html><head></head><body><div id="container"><svg width="1100" height="350"><g></g></svg></div></body></html>


/* SET UP CONNECTIONS */

mongoose.connect('mongodb://localhost:27017/orcid', {useNewUrlParser: true}) //connect to 'orcid' database
var db = mongoose.connection
var coll = 'topic'  //name of collection in MongoDB with topics for ORCIDs

db.on('error', console.error.bind(console, 'connection error:'))
db.once('open', function() { console.log('connected') })

var ORCIDschema = new mongoose.Schema({'ORCID': String,'TOPICS': Array}, {collection : coll }) //TOPICS - dictionary of words with frequencies of appearance
var ORCIDmodel = mongoose.model('ORCID', ORCIDschema)


startHTTPServer() //run http server






/* FUNCTIONS */

function startHTTPServer()
{   
    http.createServer(async function (req, res) 
    {
        res.setHeader('Access-Control-Allow-Origin', '*');
        res.setHeader('Access-Control-Request-Method', '*');
        res.setHeader('Access-Control-Allow-Methods', 'GET');
        res.setHeader('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept, Authorization');
        var query = req.url.replace('/','')

        if (fs.existsSync(dir + query + format)) //if image already created then read it, else generate new
        {
        	readFileAndRespond(query, format, res)
    	}
    	else
    	{
	        var dataFromMongo = await findDoc(ORCIDmodel, { 'ORCID': query }) //find document in database
	        var result = returnResult(dataFromMongo) //get data from database
	        
	        if (result != 'fail') //if there is no errors read file and and send response, else send not found
	        {
				readFileAndRespond(query, format, res)
	        }
	        else
	        {
	        	res.writeHead(404, {'Content-Type': 'text/plain'}) 
	        	res.end()
	    	} 
        }
    }).listen(8081)
}



function findDoc(model, query) 
{
	//Look for document in MongoDB collection
    return new Promise(function(resolve,reject)
    {
        model.findOne(query, function(err, data)
        { 
        	if (err){ console.log(err) }
			resolve(data)
        })
    })
}

function readFileAndRespond(query, format, res)
{
    //if image is already generated read it and send as response
    fs.readFile(dir + query + format, function(err, data)
    {
        if (err){ console.log(err) }
        res.writeHead(200, {'Content-Type': 'image/svg+xml'}) 
        res.write(data)
        res.end()
    })
}


/* DATA PROCESSING FUNCTIONS  */

function returnResult(inputData) 
{
	//handler for drawWordCloud function
	if (inputData == null) { return 'fail' }
    var name = inputData['ORCID']
    var wordEntries = inputData['TOPICS'].slice(0,101) //limit size of input data, because > 100 topics won't fit anyway
    drawWordCloud(wordEntries, name)
	fs.writeFileSync(dir + name + format, d3n.svgString())
	return 'success'
}

function drawWordCloud(wordEntries, name)
{
    //console.log(wordEntries)
    var arrLen = wordEntries.length
	var freqMinMax = getMinMax(wordEntries, arrLen) //get min and max frequencies of appearance
	var fontSizeMinMax = []//array min and max font size
	var width = 1100
    var height = 350
    
    //adapt font size to the number of topics 
	if (arrLen > 40)
	{
        if (arrLen > 100)
        	{ 
        		fontSizeMinMax = [18,35] 
        		height = 400
        	}
        else if (arrLen > 80)
        	{ 
        		fontSizeMinMax = [18, 45] 
        		height = 380
        	}   
        else if (arrLen > 60)
        	{ 
        		fontSizeMinMax = [18, 50] 
        		height = 360
        	}
        else 
        	{ 
        		fontSizeMinMax = [18, 60] 
        		height = 350
        	}	
    }
	else
	{       
        if (arrLen < 20)
        {
        	fontSizeMinMax = [20,50]
        	height = 300
        }
        else
        { 
        	fontSizeMinMax = [20,50] 
        	height = 350
        } // 20-40
	}
    
 
    if (freqMinMax[1] - freqMinMax[0] > numColors)  
    {
        //Entries that have small range between min and max frequencies return mostly monochrome images
        //We need to shift min frequency by some constant (-1/2 of arrLen) so colors are distributed much better
        //In case if difference betwee max frequency and min frequency is less than number of colors, 
        //then colors should be distributed okay
        freqMinMax[0] = -Math.round(arrLen / 2) 
    }
    
    
	d3.select(d3n.document.querySelector('#container')).select('svg').attr('height', height)
	var halfw = width/2
    var halfh = height/2  
    
	
    var fill = d3.scaleQuantize()
					.domain(freqMinMax)
					.range(colors)
	
	var xScale = d3.scaleLinear()
					.domain(freqMinMax)
					.range(fontSizeMinMax)



	cloud().size([width, height])
		.canvas(function() { return new Canvas.Canvas(width, height) })
		.words(wordEntries)
		.padding(2) //padding between words
		.rotate(0) // we don't need verticaly positioned words
		.font('Impact')
		.fontSize(function(d) { return textSize(d) })
		.text(function(d) { return d.key })
		.spiral('rectangular')//'archimedean' or 'rectangular'
		.on('end', draw)
		.start()
	

	cloud().stop() 
	
	function textSize(word)
	{
		//If the length of the text is too big it won't be displayed on the image
		//That's why we need to decrease size of text if its length is more than width of canvas
		var size = xScale(word.value)
		if (((word.key.length * size) / 2) > (width / 3)) //coefficient 2 estimated for Impact font
		{
			return ((width / word.key.length) / 2) *1.5
		}
		else{ return size }		
	}
	
	function draw(words) 
	{
		svg.selectAll('text').remove() //remove previous text
		svg
		.selectAll('text')
		.data(words)
		.enter()
		.append('text')
		.style('font-size', function(d) { return textSize(d) + 'px' })
		.style('font-family', 'Impact')
		.style('fill', function(d) { return fill(d.value) })
		.style('stroke','black')
		.style('stroke-width','0.2')
		.style('stroke-linecap','round')
		.attr('text-anchor', 'middle')
		.attr('transform', function(d) 
			{
				return 'translate(' + [d.x + halfw, d.y + halfh] + ')'
			})
		.text(function(d) { return d.key })
		.exit()	
    }
}

function getMinMax(data, len)
{
    //get min and max values of this list of dictionaries
    //In the input data the max value is always the first and min is always last
    
    return [data[len-1]['value'], data[0]['value']] //min,max
}