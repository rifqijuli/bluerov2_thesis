class click_mouse_position:
    x = 0
    y = 0

    def set_position(x_pos, y_pos):
        click_mouse_position.x = x_pos
        click_mouse_position.y = y_pos
    
    def is_within_object(object):
        #log.info(f"Object coords and size: X={object['x_coord']}, Y={object['y_coord']}, Width={object['width']}, Height={object['height']}")
        #log.info(f"Mouse Poisition: X={click_mouse_position.x}, Y={click_mouse_position.y}")
        return (
            click_mouse_position.x >= object['x_coord'] and
            click_mouse_position.x <= object['x_coord'] + object['width'] and
            click_mouse_position.y >= object['y_coord'] and
            click_mouse_position.y <= object['y_coord'] + object['height']
        )
    def reset():
        click_mouse_position.x = 0
        click_mouse_position.y = 0