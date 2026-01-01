This is a basic script used for converting one input sheet in one format to another format. Additonally, there is modular post processing for getting the data into the final desired output.

Most data conversion is not simply one to one mappings of columns. There are an infinite setup possibilites for sheets for all different purposes. This script was created to easily convert production music library album data to different output formats. This process was often complicated, but once the template was set up one time, it could be reused with ease.

The templates are stored in JSON format so multiple templates can easily be stored together, versioned, and maintained. Each template consists of 4 keys:
  - Template Name
  - Template Version
  - Header Map : a dictionary where the key is the source header and the value is the destination header.
  - Post Process Config : a set of transforms represented by an ID and the arguments for that post process function.

The templates are desined to be unidirectional. One input is set up to export to one output and have a predetermined post processing executed on the output data. This intentionally done this way because most often, libraries have a set number of sheets that they need for any given album. These sheets very rarely change and due to the nature of album metadata, each process should occur the exact same way every time. To add backwards compatibility and a more complex templating structure would cause noise and be overengineered for what the vast majority of libraies need.


The flow of the pipeline is straightforward:
  - The template JSON is read and the component pieces are extracted
  - The input data is loaded
  - The output dataframe is constructed using the headers form the template header map
  - The input data headers are mapped to the output dataframe
  - Post processing is carried out on the output datafrmae
  - Output dataframe is saved to disk
    
