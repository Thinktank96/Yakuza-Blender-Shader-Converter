# Yakuza Imported Proprietary Shader to Blender Principled Shader Conversion Script v. 2.0
# 
# Just run this script from inside your project and it will find all the matching 
# materials and convert them to use principled bsdf instead. (Currently it only will convert diffuse and normal maps, without handling compression)
#
#
# This script created by Riley Leal (Thinktank)
# You can find me at @_StudioElephant on twitter and @studio.elephant.software on instagram or rileyleal@outlook.com.

import bpy

def change_materials(obj):
    # Check if the object can have materials
    if obj is not None and obj.type == 'MESH':
        
        print(f"Found a mesh: {obj.name}")
        
        # Check if the object has any materials
        if len(obj.data.materials) > 0:
            
            print(f"-Checking materials for object: {obj.name}")
            
            # Iterate over each material in the object
            for material_slot in obj.material_slots:
                material = material_slot.material
                
                print(f"--Material: {material.name}")
                
                # Check if the material has a shader node tree
                if material.use_nodes:
                    tree = material.node_tree
                    print(f"---Nodes used")
                    
                    # Store the old non-BSDF node and its corresponding texture input
                    old_node = None
                    old_diffuse_input = None
                    old_multimap_input = None
                    old_normal_input = None
                    
                    # Iterate over each node in the shader node tree
                    for node in tree.nodes:
                        
                        print(f"----Node: {node.type}")
                        
                        # Check if the node is a shader node
                        if node.type == 'GROUP': # if you don't know what this is called, just run the script and it will give you a list of all nodes on the material
                            print(f"----Shader node: {node.bl_idname}")
                            # Check if the node is not a BSDF shader node
                            if node.bl_idname != 'ShaderNodeBsdfPrincipled':
                                # Store the old non-BSDF node and its texture input
                                old_node = node
                                old_diffuse_input = node.inputs['texture_diffuse']
                                old_multimap_input = node.inputs['texture_multi']
                                old_normal_input = node.inputs['texture_normal']
                                print(f"-----Found a Yakuza shader node: {old_node.name}")
                    
                    # Check if an old non-BSDF node and its texture input were found
                    if old_node is not None and old_diffuse_input is not None:
                        # Create a new Principled BSDF node
                        new_node = tree.nodes.new('ShaderNodeBsdfPrincipled')
                        new_node.location = (old_node.location.x + 300, old_node.location.y)  # Example: Position the new node
                        
                        # Set the new shader properties from the new node
                        new_diffuse_input = new_node.inputs['Base Color']
                        new_metallic_input = new_node.inputs['Metallic']
                        new_specular_input = new_node.inputs['Specular']
                        new_roughness_input = new_node.inputs['Roughness']
                        new_normal_input = new_node.inputs['Normal']
                        
                        # Reassign the texture input to the new shader
                        if old_diffuse_input.links:
                            tree.links.new(old_diffuse_input.links[0].from_socket, new_diffuse_input)
                        
                        if old_multimap_input is not None and old_multimap_input.links:
                            # currently, the person I'm writing this for has no need for the multimaps to be 
                            # converted to usable maps by blender, but I will leave the injection point for 
                            # that code here for future.
                            
                            print(f"-----Ignoring multi texture currently")
                            #tree.links.new(old_multimap_input.links[0].from_socket, new_multimap_input)
                            
                        if old_normal_input is not None and old_normal_input.links:
                            normal_map_node = tree.nodes.new("ShaderNodeNormalMap")
                            normal_map_node.location = (old_node.location.x + 150, old_node.location.y - 200)
                            # some of the normal maps are compressed, and can be apparently decompressed by simply adding
                            # a blue channel back and setting it to 1.0f. I will not be doing this in this version because 
                            # I don't know if the person I am writing this for actually needs that, though I will leave
                            # this note here for myself if I need to in a future version.
                            tree.links.new(old_normal_input.links[0].from_socket, normal_map_node.inputs['Color'])
                            tree.links.new(normal_map_node.outputs['Normal'], new_normal_input)
                        
                        # Connect the new shader to the Material Output node
                        output_node = None
                        for node in tree.nodes:
                            if node.type == 'OUTPUT_MATERIAL':
                                output_node = node
                                break
                        if output_node is not None:
                            tree.links.new(new_node.outputs['BSDF'], output_node.inputs['Surface'])
                        
                        # Remove the old non-BSDF node
                        tree.nodes.remove(old_node)
                
                # Update the material to reflect the changes
                material.update_tag()


# Iterate through every object in the scene
for obj in bpy.data.objects:
    # Call the function to change materials for each object
    print(f"Checking object: {obj.name}")
    change_materials(obj)
