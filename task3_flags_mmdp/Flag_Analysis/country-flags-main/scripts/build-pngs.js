var process = require('process')
var exec = require('child_process').exec
var fs = require('fs')
var path = require('path')

var help_message = "You must pass one argument to build-pngs. It should be target dimension in the format `200:` for width 200px, or `:200` for height 200px."
var svg_directory = 'svg/'

// Check arguments
function get_output_directory() {
    // Replace : with x, if two dimensions are specified
    var dim = process.argv[2].split(':').filter(x => x.length > 0)
    var dir = 'png' + (dim.length > 1 ? dim.join('x') : dim) + 'px'

    return dir
}

function get_output_dimensions() {
    return process.argv[2]
}

function check_arguments(callback) {
    if (process.argv.length != 3) {
        console.log(help_message)
        process.exit(1)
    }

    var dimensions = process.argv[2]
    if (/^[0-9]*:[0-9]*$/.test(dimensions) && dimensions.length > 2) {
        var output_folder = get_output_directory()
        console.log("Output folder: " + output_folder)
        
        if (!fs.existsSync(output_folder)){
            fs.mkdirSync(output_folder)
        }

        callback()
    }
    else {
        console.log(help_message)
        process.exit(1)
    }
}

function check_for_svgexport(callback) {
    // Check for presence of imagemin-cli and svgexport
    console.log("Checking if `svgexport` is available...")
    exec('svgexport', function(error, stdout, stderr) {
        if (stdout.indexOf("Usage: svgexport") !== -1) {
            callback()
        }
        else {
            console.log("`svgexport` is not installed.")
            console.log("Please run: npm install -g svgexport")
            process.exit(1)
        }
    })
}

function check_for_imagemin(callback) {
    // Check for presence of imagemin-cli
    console.log("Checking if `imagemin-cli` is available...")
    exec("imagemin --version", function(error, stdout, stderr) {
        if (!error) {
            callback()
        }
        else {
            console.log("`imagemin-cli` is not installed.")
            console.log("Please run: npm install -g imagemin-cli")
            process.exit(1)
        }
    })
}

function get_all_svgs(callback) {
    fs.readdir(svg_directory, function(err, items) {
        if (err) {
            console.log("Could not list *.svg files. Check your working directory.")
            process.exit(1)
        }

        // ✅ Now accept ANY file name (with spaces, capitals, etc.)
        items = items.filter(file => file.endsWith('.svg'))

        if (items.length === 0) {
            console.log("No SVG files found in the folder.")
            process.exit(1)
        }

        callback(items)
    })
}

function convert_and_compress_svg(file_name, callback) {
    var input_path = path.join(svg_directory, file_name)
    var output_path = path.join(get_output_directory(), file_name.replace('.svg', '.png'))

    // ✅ Handle files with spaces by wrapping them in quotes
    var svgexport_command = `svgexport "${input_path}" "${output_path}" pad ${get_output_dimensions()}`
    console.log(svgexport_command)
    
    exec(svgexport_command, (error, stdout, stderr) => {
        if (error) {
            console.log("Failed to convert SVG: " + file_name)
            process.exit(1)
        }

        // ✅ Compress the image
        var image_min_command = `imagemin "${output_path}" --out-dir=${get_output_directory()}`
        console.log(image_min_command)
        exec(image_min_command, (error, stdout, stderr) => {
            if (error) {
                console.log("Failed to compress PNG: " + file_name)
                process.exit(1)
            }

            callback()
        })
    })
}

function convert_all_files(svgs, callback) {
    var i = 0

    function do_next_file() {
        if (i >= svgs.length) {
            callback()
            return
        }

        console.log("Converting [" + (i+1) + "/" + svgs.length + "] " + svgs[i])
        convert_and_compress_svg(svgs[i], () => {
            i++
            do_next_file()
        })
    }

    do_next_file()
}

// Run the program
check_arguments(() =>
    check_for_imagemin(() =>
    check_for_svgexport(() =>
    get_all_svgs((svgs) => convert_all_files(svgs, () => {
        console.log("✅ All SVGs converted to PNG!")
        process.exit(0)
    })
))))
var process = require('process')
var exec = require('child_process').exec
var fs = require('fs')
var path = require('path')

var help_message = "You must pass one argument to build-pngs. It should be target dimension in the format `200:` for width 200px, or `:200` for height 200px."
var svg_directory = 'svg/'

// Check arguments
function get_output_directory() {
    // Replace : with x, if two dimensions are specified
    var dim = process.argv[2].split(':').filter(x => x.length > 0)
    var dir = 'png' + (dim.length > 1 ? dim.join('x') : dim) + 'px'

    return dir
}

function get_output_dimensions() {
    return process.argv[2]
}

function check_arguments(callback) {
    if (process.argv.length != 3) {
        console.log(help_message)
        process.exit(1)
    }

    var dimensions = process.argv[2]
    if (/^[0-9]*:[0-9]*$/.test(dimensions) && dimensions.length > 2) {
        var output_folder = get_output_directory()
        console.log("Output folder: " + output_folder)
        
        if (!fs.existsSync(output_folder)){
            fs.mkdirSync(output_folder)
        }

        callback()
    }
    else {
        console.log(help_message)
        process.exit(1)
    }
}

function check_for_svgexport(callback) {
    // Check for presence of imagemin-cli and svgexport
    console.log("Checking if `svgexport` is available...")
    exec('svgexport', function(error, stdout, stderr) {
        if (stdout.indexOf("Usage: svgexport") !== -1) {
            callback()
        }
        else {
            console.log("`svgexport` is not installed.")
            console.log("Please run: npm install -g svgexport")
            process.exit(1)
        }
    })
}

function check_for_imagemin(callback) {
    // Check for presence of imagemin-cli
    console.log("Checking if `imagemin-cli` is available...")
    exec("imagemin --version", function(error, stdout, stderr) {
        if (!error) {
            callback()
        }
        else {
            console.log("`imagemin-cli` is not installed.")
            console.log("Please run: npm install -g imagemin-cli")
            process.exit(1)
        }
    })
}

function get_all_svgs(callback) {
    fs.readdir(svg_directory, function(err, items) {
        if (err) {
            console.log("Could not list *.svg files. Check your working directory.")
            process.exit(1)
        }

        // ✅ Now accept ANY file name (with spaces, capitals, etc.)
        items = items.filter(file => file.endsWith('.svg'))

        if (items.length === 0) {
            console.log("No SVG files found in the folder.")
            process.exit(1)
        }

        callback(items)
    })
}

function convert_and_compress_svg(file_name, callback) {
    var input_path = path.join(svg_directory, file_name)
    var output_path = path.join(get_output_directory(), file_name.replace('.svg', '.png'))

    // ✅ Handle files with spaces by wrapping them in quotes
    var svgexport_command = `svgexport "${input_path}" "${output_path}" pad ${get_output_dimensions()}`
    console.log(svgexport_command)
    
    exec(svgexport_command, (error, stdout, stderr) => {
        if (error) {
            console.log("Failed to convert SVG: " + file_name)
            process.exit(1)
        }

        // ✅ Compress the image
        var image_min_command = `imagemin "${output_path}" --out-dir=${get_output_directory()}`
        console.log(image_min_command)
        exec(image_min_command, (error, stdout, stderr) => {
            if (error) {
                console.log("Failed to compress PNG: " + file_name)
                process.exit(1)
            }

            callback()
        })
    })
}

function convert_all_files(svgs, callback) {
    var i = 0

    function do_next_file() {
        if (i >= svgs.length) {
            callback()
            return
        }

        console.log("Converting [" + (i+1) + "/" + svgs.length + "] " + svgs[i])
        convert_and_compress_svg(svgs[i], () => {
            i++
            do_next_file()
        })
    }

    do_next_file()
}

// Run the program
check_arguments(() =>
    check_for_imagemin(() =>
    check_for_svgexport(() =>
    get_all_svgs((svgs) => convert_all_files(svgs, () => {
        console.log("✅ All SVGs converted to PNG!")
        process.exit(0)
    })
))))
