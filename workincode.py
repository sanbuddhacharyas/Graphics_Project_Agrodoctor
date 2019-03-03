import glfw
from OpenGL.GL import *
import ShaderLoader
import numpy
import pyrr
from PIL import Image 
from ObjLoader import *
import time
from pygame import mixer

first_mouse = True
key_pressed = True
i_x =0
i_y = 0
shift_left =0
shift_top =0
rot_y = pyrr.Matrix44.from_y_rotation(0.002 * i_y )
rot_x = pyrr.Matrix44.from_x_rotation(0.002 * i_x )
x = 0
y = 0 
zoom = 45
w_width, w_height = 1280,720

def window_resize(window, width, height):
    glViewport(0, 0, width, height)

def prespecive_projection(shader,zoom,w_width, w_height, x ,y ,z):
    view = pyrr.matrix44.create_from_translation(pyrr.Vector3([x , y, z]))
    projection = pyrr.matrix44.create_perspective_projection_matrix(zoom , w_width / w_height, 0.1, 100.0)
    model = pyrr.matrix44.create_from_translation(pyrr.Vector3([0, 0, 0]))

    view_loc = glGetUniformLocation(shader, "view")
    proj_loc = glGetUniformLocation(shader, "projection")
    model_loc = glGetUniformLocation(shader, "model")

    glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)
    glUniformMatrix4fv(proj_loc, 1, GL_FALSE, projection)
    glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)


def mouse_callback(window, xpos, ypos):
    global first_mouse, lastX, lastY
    global i_y,rot_y,i_x,rot_x,zoom,  w_width, w_height,shift_left ,x ,y,key_pressed

    if first_mouse:
        lastX = xpos
        lastY = ypos
        first_mouse = False

    xoffset = xpos - lastX
    yoffset = lastY - ypos

    lastX = xpos
    lastY = ypos

   
    if  glfw.get_mouse_button(window,glfw.MOUSE_BUTTON_3) == glfw.PRESS:
        x += xoffset*0.001
        y += yoffset*0.001
    else:
        i_y += yoffset
        i_x += xoffset
        rot_y = pyrr.Matrix44.from_y_rotation(0.002 * i_x )
        rot_x = pyrr.Matrix44.from_x_rotation(0.002 * i_y )

    print("xoffset==>"+str(xoffset)+" yoffset"+str(yoffset))

def scroll_callback(window , xpos ,ypos):
    global zoom
    ypos = -ypos
    zoom += ypos 
    print("xpos"+str(xpos)+"ypos"+str(ypos))
       
def object_load(model_ID ,VBO):
    texture_offset = len(model_ID.vertex_index)*12
    normal_offset = (texture_offset + len(model_ID.texture_index)* 8)

    glBindVertexArray(VBO)

    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, model_ID.model.itemsize * len(model_ID.model), model_ID.model, GL_STATIC_DRAW)



    #position
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, model_ID.model.itemsize * 3, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)
    
    #texture
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, model_ID.model.itemsize * 2, ctypes.c_void_p(texture_offset))
    glEnableVertexAttribArray(1)

    #normal
    glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, model_ID.model.itemsize * 3, ctypes.c_void_p(normal_offset))
    glEnableVertexAttribArray(2)



def main():
    global x ,y
    z = -9
    global rot_y,i_x,i_y,rot_x,zoom
    string ="/home/sansii/Desktop/Robotic_ARM_Simulation/"
    mixer.init()
    mixer.music.load(string+"audio/starting3.mp3")
   
    # initialize glfw
    if not glfw.init():
        return
    
    w_width, w_height = 1280,720
    glfw.window_hint(glfw.RESIZABLE, GL_FALSE)
    window = glfw.create_window(w_width, w_height, "Agro_Doctor", None, None)

    if not window:
        glfw.terminate()
        return


    glfw.make_context_current(window)
    glfw.set_window_size_callback(window, window_resize)

    
    #Modeling loading
    obj = ObjLoader()
    cube = ObjLoader()
    obj.load_model(string +"res/frustu.obj")
    cube.load_model(string+"res/cube_intro.obj")
   
    """
        Loading vertex shader and fragment shader from file and both shaders are compiled and linked with common shader program(shader)
    """
    shader = ShaderLoader.compile_shader(string+"shaders/video_18_vert.vs", string+"shaders/video_18_frag.fs")
    VBO = glGenVertexArrays(2)

    #**********For Robort Model*****************
    object_load(obj, VBO[0])
    
    #***********Ending_OF_Robot_Model*****************


    #**********Cube*****************
    object_load(cube,VBO[1])

    #***********Ending_OF_CUBE_MODEL*****************



    #set key eventBind our texture in Texture Unit 0
    glfw.set_input_mode(window,glfw.STICKY_KEYS,GL_TRUE) 
    glfw.set_cursor_pos_callback(window, mouse_callback)
    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
    glfw.set_input_mode(window,glfw.STICKY_MOUSE_BUTTONS,GL_TRUE)
    glfw.set_scroll_callback(window, scroll_callback)
    #**************CallBack_Function_End***************
    
    

    
    #*********LOADING TEXTURE**************
    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)

    # Set the texture wrapping parameters
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

    # Set texture filtering paraGL_TEXTURE_2Dmeters
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    # load image
    
    images_array = np.load(string+'full_working.npy')
    image = Image.open(string+"res/800-640_jpg.jpg")
    flipped_image = image.transpose(Image.FLIP_TOP_BOTTOM)
    img_data = numpy.array(list(flipped_image.getdata()), numpy.uint8)

    #*********Ending TEXTURE****************
    

    glUseProgram(shader) #this function activates the created shader in our main program
    glClearColor(0.2, 0.3, 0.2, 1.0)
    glEnable(GL_DEPTH_TEST)


    glBindVertexArray(VBO[0])
    prespecive_projection(shader,50, w_width, w_height, x,y,-2)
    
    o = 372
    
    mixer.music.play(2)
    i_yy = 0
    i_xx = 0
    increment = -5
    m = False

    while not glfw.window_should_close(window):
        glfw.poll_events()
        if o < images_array.shape[0]-1:
            rot_yy = pyrr.Matrix44.from_y_rotation(0.1* i_yy )
            rot_xx = pyrr.Matrix44.from_x_rotation(0.1 * i_xx )
            prespecive_projection(shader,zoom, w_width, w_height,x ,y ,increment)
            glBindVertexArray(VBO[1])
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, 800, 600, 0, GL_RGB, GL_UNSIGNED_BYTE,images_array[o])
            glEnable(GL_TEXTURE_2D)
            glClearColor(0.2, 0.3, 0.2, 1.0)
            glEnable(GL_DEPTH_TEST)  
            transformLoc = glGetUniformLocation(shader, "transform")
            glUniformMatrix4fv(transformLoc, 1, GL_FALSE, numpy.array(rot_xx * rot_yy  ))
            i_yy += 0.2
            i_xx -= 0.2
            o += 1 
            if increment > -3:
                m = True
            
            if m==True:
                increment -= 0.01
            else:
                increment += 0.01

            time.sleep(0.033333)

        else:
            glBindVertexArray(VBO[0])
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, image.width, image.height, 0, GL_RGB, GL_UNSIGNED_BYTE,img_data)
            glEnable(GL_TEXTURE_2D)
            glClearColor(0.2, 0.3, 0.2, 1.0)
            glEnable(GL_DEPTH_TEST)  
            prespecive_projection(shader,zoom, w_width, w_height,x ,y ,-5)
            transformLoc = glGetUniformLocation(shader, "transform")
            light_loc = glGetUniformLocation(shader,"light")
            glUniformMatrix4fv(light_loc, 1, GL_FALSE, numpy.array(rot_x * rot_y))
            glUniformMatrix4fv(transformLoc, 1, GL_FALSE, numpy.array(rot_x * rot_y ))

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glDrawArrays(GL_TRIANGLES, 0, len(obj.vertex_index))
       
        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == "__main__":
    main()


