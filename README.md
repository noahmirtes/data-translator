This is a basic script used for converting one input sheet in one format to another format. Additonally, there is modular post processing for getting the data into the final desired output.

Most data conversion is not simply one to one mappings of columns. There are an infinite setup possibilites for sheets for all different purposes. This script was created to easily convert production music library album data to different output formats. This process was often complicated, but once the template was set up one time, it could be reused with ease.

The templates are stored in JSON format so multiple templates can easily be stored together, versioned, and maintained. Each template consists of 4 keys:
  - Template Name
  - Template Version
  - Header Map : a dictionary where the key is the source header and the value is the destination header.
  - Post Process Config : a set of transforms represented by an ID and the arguments for that post process function.

The templates are desined to be unidirectional. One input is set up to export to one output and have a predetermined post processing executed on the output data. This intentionally done this way because most often, libraries have a set number of sheets that they need for any given album. These sheets very rarely change and due to the nature of album metadata, each process should occur the exact same way every time. Backwards compatability between output and input templates is intentionally excluded to keep the template structure simple, deterministic, and easy to understand. 

The flow of the pipeline is straightforward:
  - Template JSON is read, component pieces are extracted
  - The input data is loaded
  - The output dataframe is constructed using the headers from the template header map
  - The input data headers are mapped to the output dataframe
  - Post processing is executed on the output dataframe. Config is set in the JSON
  - Output dataframe is saved to disk

    
The post processing capabilities of this script are the most important component and is what allows for a wide range of output formats to be produced. Converting data from one format to another very often requires more than simple source-dest copying from one header to another. Certain columns are based on the contents of other cells in that row, so post processing capabilities are a necessity to properly reformat one sheet's data into another format.





The real world is messy and often involves compicated relationships between column values and resulting data. Therefore, the transform functions need flexibility and robustness in order to handle any possible relationship involved in post-processing. Modularity is absolutely key here!

Because of this, I've created the post processing functions to work as .apply functions on each row. Each post process function contains a nested function that operates on the row and can access header values passed in as arguments to the top level transform function. This allows for all complexity at the transform level to be cleanly isolated and readibly reusable.

