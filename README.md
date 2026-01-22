INTRO:
This is a module used for converting one input sheet in one format to another format complete with post processing capabilities to translate any input data format to any output data format.

USAGE:
Most data conversion is not simply one to one mappings of columns. There are an infinite setup possibilites for sheets for all different purposes. This script was created to easily convert production music library album data to different output formats and eliminate the need for tedious manual copying or excel macro spaghetti. 

In the production music landscape, libraries reliably need specific output sheets for every single one of their albums for registration, distribution, etc. Since the data structures very rarely change, many libraries would seriously benefit from a pipeline that allows the user to input one sheet and output any number of different formatted outputs to cover all their distribution requirements. Typically templates vary widely in micro formatting specifics, but the foundational elements of the data stay the same (eg. Track Title, Composer Info, etc). With this script, all libraries need to do is set up their templates and post processing requirements once for each template and then set it and forget it!

TRANSLATION FLOW:
The flow of the pipeline is straightforward:
  - Template JSON is read, component pieces are extracted
  - The input data is loaded
  - The output dataframe is constructed using the headers from the template header map
  - The input data headers are mapped to the output dataframe for 1:1 columns and to pre-seed columns for post processing should they need it
  - Post processing is executed on the output dataframe. Config is set in the JSON
  - Output dataframe is saved to disk

  - 
TEMPLATES:
The input/output templates are stored in JSON format so multiple templates can easily be stored in a unified location making versioning and maintenance easy. Each template consists of 4 keys:
  - Template Name
  - Template Version
  - Header Map : a dictionary where the key is the source header and the value is the destination header.
  - Post Process Config : a set of transforms represented by an ID and the arguments for that post process function.

The templates are desined to be unidirectional. One input is set up to export to one output and have a predetermined post processing executed on the output data. This intentionally done this way because most often, libraries have a set number of sheets that they need for any given album. These sheets very rarely change and due to the nature of album metadata, each process should occur the exact same way every time. Backwards compatability between output and input templates is intentionally excluded to keep the template structure simple, deterministic, and easy to understand. 



POST PROCESSING:
The post processing capabilities of this script are the most important component and is what allows for a wide range of output formats to be produced. Converting data from one format to another very often requires more than simple source-dest copying from one header to another. Certain columns are based on the contents of other cells in that row (or column), so post processing capabilities are a necessity to properly reformat one sheet's data into another format. Because of these complexities that arise when working with multiple different types of real world templates, the transform functions need flexibility and robustness in order to handle any possible relationship involved in post-processing. Modularity is absolutely key here!

Because of this, I've created the post processing functions to work as .apply functions on each row. Each post process function contains a nested function that operates on the row and can access header values passed in as arguments to the top level transform function. This allows for all complexity at the transform level to be cleanly isolated and readibly reusable. By conceding to the tradeoff of tight modularity, you get very high flexiblity and control over post processes.

The post processingThis is how the post processing config is set up in the template json file:


All of the functions in my post_process.py file are things I used on real data, but are very specific to just those albums and their unique formats. It is very likely any other user would need to modify and create other post processes in order to meet their specific template's needs.

While this was created for production library music data, it can be used on any tabular data in a specified format. For non production music applications, post processing could even be less complicated, requiring fewer rule based / filtering approaches to get the final data in the right shape.
