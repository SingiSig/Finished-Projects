#!/usr/bin/env python
import rospy
import actionlib
import math
import time
import tf2_ros
import tf_conversions
import cv2
import numpy
from geometry_msgs.msg import Twist
from moveit_python import MoveGroupInterface, PlanningSceneInterface
from geometry_msgs.msg import PoseStamped, Pose, Point, Quaternion
from moveit_msgs.msg import MoveItErrorCodes
from control_msgs.msg import (FollowJointTrajectoryAction,
                              FollowJointTrajectoryGoal,
                              GripperCommandAction,
                              GripperCommandGoal)
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from opencv_apps.msg import MomentArrayStamped 
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
from geometry_msgs.msg import TransformStamped


joint_names = ["torso_lift_joint", "shoulder_pan_joint",
                   "shoulder_lift_joint", "upperarm_roll_joint",
                   "elbow_flex_joint", "forearm_roll_joint",
                   "wrist_flex_joint", "wrist_roll_joint"]
joint_positions = [0.350, 1.4, -0.8, 0.4, -1.0, -1.9, 1.9, -0.4]

re_joint_names = ["torso_lift_joint", "shoulder_pan_joint",
                   "shoulder_lift_joint", "upperarm_roll_joint",
                   "elbow_flex_joint", "forearm_roll_joint",
                   "wrist_flex_joint", "wrist_roll_joint"]
re_joint_positions = [0.350, 0.3, -0.9, 0.02, 0.8, -0.05, 1.7, 0.0]

head_joint = ["head_pan_joint", "head_tilt_joint"]

head_pose = [0.0, 0.500]

re_head_joint = ["head_pan_joint", "head_tilt_joint"]

re_head_pose = [0.0, 0.0]

def globalVariables():
    global foundCube
    foundCube = False
    global foundBin
    foundBin = False
    global move_group
    move_group = MoveGroupInterface("arm_with_torso", "base_link")
    global head_client
    head_client = actionlib.SimpleActionClient("head_controller/follow_joint_trajectory", FollowJointTrajectoryAction)
    global pub
    pub = rospy.Publisher('/cmd_vel', Twist, queue_size=1000)
    global msg
    msg = Twist()
    global rate
    rate = rospy.Rate(2)
    global x # horisontal x>0
    x=0
    global y # vertical y>400
    y=0
    global areaC
    areaC = 0
    global areaTHC
    areaTHC = 1000
    global areaB
    areaB = 0
    global areaTHB
    areaTHB = 5
    global gripper_open
    gripper_open = 0.05
    global gripper_closed
    gripper_closed = 0.00
  
  
def goalDone_cb(state, done):
    rospy.loginfo('goal done')
    
def active_cb():
    rospy.loginfo('goal active')
    
def feedback_cb():
    rospy.logdebug('goal progress %s', fb.base_position.pose)

def depthPerception(image):
    global x, y
    bridge = CvBridge() #global
    # image obtained from callback message for topic
    try:
        cv_image = bridge.imgmsg_to_cv2(image, "32FC1")
        # where x,y is the centre point from the published moment
        depth = cv_image[y][x] #global
        # For testing/verification:
        cv2.circle(cv_image, (x,y), 10, 255) # draw circle radius 10 at x,y
        cv2.imshow("Image window", cv_image) # display the image
        cv2.waitKey(3)
        br = tf2_ros.TransformBroadcaster()
        
        t = TransformStamped()

        t.header.stamp = rospy.Time.now()
        t.header.frame_id = "head_camera_depth_frame"
        t.child_frame_id = "target_object"
        t.transform.translation.x = depth
        t.transform.translation.y = 0 #-x_offset from pixel to meter
        t.transform.translation.z = 0 #-y_offset
        q = tf_conversions.transformations.quaternion_from_euler(0, 0.5*math.pi, 0)
        t.transform.rotation.x = q[0]
        t.transform.rotation.y = q[1]
        t.transform.rotation.z = q[2]
        t.transform.rotation.w = q[3]

        br.sendTransform(t)
        
        
    except CvBridgeError as e:
        print(e)

def readyHead():
    global head_client
    head_client.wait_for_server()
    
    trajectory = JointTrajectory()
    trajectory.joint_names = head_joint
    trajectory.points.append(JointTrajectoryPoint())
    trajectory.points[0].positions = head_pose
    trajectory.points[0].velocities = [0.0] * len(head_pose)
    trajectory.points[0].accelerations = [0.0] * len(head_pose)
    trajectory.points[0].time_from_start = rospy.Duration(5.0)

    head_goal = FollowJointTrajectoryGoal()
    head_goal.trajectory = trajectory
    head_goal.goal_time_tolerance = rospy.Duration(0.0)

    rospy.loginfo("Setting positions...")
    head_client.send_goal(head_goal)
    head_client.wait_for_result(rospy.Duration(6.0)) 
    rospy.loginfo("...done")

def resetHead():
    global head_client
    head_client.wait_for_server()
    
    trajectory = JointTrajectory()
    trajectory.joint_names = re_head_joint
    trajectory.points.append(JointTrajectoryPoint())
    trajectory.points[0].positions = re_head_pose
    trajectory.points[0].velocities = [0.0] * len(re_head_pose)
    trajectory.points[0].accelerations = [0.0] * len(re_head_pose)
    trajectory.points[0].time_from_start = rospy.Duration(5.0)

    head_goal = FollowJointTrajectoryGoal()
    head_goal.trajectory = trajectory
    head_goal.goal_time_tolerance = rospy.Duration(0.0)

    rospy.loginfo("Setting positions...")
    head_client.send_goal(head_goal)
    head_client.wait_for_result(rospy.Duration(6.0)) 
    rospy.loginfo("...done")

def readyUpBody():
    
    global move_group
    move_group.moveToJointPosition(joint_names, joint_positions, wait=False)

    # Since we passed in wait=False above we need to wait here
    move_group.get_move_action().wait_for_result()
    result = move_group.get_move_action().get_result()

    if result:
        # Checking the MoveItErrorCode
        if result.error_code.val == MoveItErrorCodes.SUCCESS:
            rospy.loginfo("Disco!")
        else:
            # If you get to this point please search for:
            # moveit_msgs/MoveItErrorCodes.msg
            rospy.logerr("Arm goal in state: %s",
                         move_group.get_move_action().get_state())
    else:
        rospy.logerr("MoveIt! failure no result returned.")
    
    move_group.get_move_action().cancel_all_goals()

#def pickUp():
    '''    
    global move_group, gripper_open, rate
    
    rospy.loginfo("Waiting for gripper_controller...")
    gripper_client = actionlib.SimpleActionClient("gripper_controller/gripper_action", GripperCommandAction)
    gripper_client.wait_for_server()
    rospy.loginfo("...connected.")
    gripper_goal = GripperCommandGoal()
    gripper_goal.command.max_effort = 10.0
    gripper_goal.command.position = gripper_open

    rospy.loginfo("Setting positions closed...")
    gripper_client.send_goal(gripper_goal)
    gripper_client.wait_for_result(rospy.Duration(5.0))
    
    tfBuffer = tf2_ros.Buffer()
    listener = tf2_ros.TransformListener(tfBuffer)
    
    while True:
        try:
            trans = tfBuffer.lookup_transform('base_link', 'target_object', rospy.Time())
            break
        except (tf2_ros.LookupException, tf2_ros.ConnectivityException, tf2_ros.ExtrapolationException):
            rate.sleep()
            continue
    x=trans.transform.translation.x
    y=trans.transform.translation.y
    z=trans.transform.translation.z
    
    q = tf_conversions.transformations.quaternion_from_euler(0, 0.5*math.pi, 0)
    grip_frame = 'wrist_roll_link'
    
    grip = [Pose(Point(x, y, z+0.5), Quaternion(q[0], q[1], q[2], q[3])),\
    Pose(Point(x, y, z+0.3), Quaternion(q[0], q[1], q[2], q[3])),\
    Pose(Point(x, y, z+0.1), Quaternion(q[0], q[1], q[2], q[3]))]
    
    print grip
    
    gripper_pose_stamped = PoseStamped()
    gripper_pose_stamped.header.frame_id = 'base_link'
    
    for pose in grip:
        gripper_pose_stamped.header.stamp = rospy.Time.now()
        gripper_pose_stamped.pose = pose
        move_group.moveToPose(gripper_pose_stamped, grip_frame)
        
    move_group.get_move_action().Cancel_all_goals()
    
    time.sleep(2)
    '''
def pickUp():
    move_group.moveToJointPosition(re_joint_names, re_joint_positions, wait=False)
    
    
    tfBuffer = tf2_ros.Buffer()
    # Since we passed in wait=False above we need to wait here
    move_group.get_move_action().wait_for_result()
    result = move_group.get_move_action().get_result()
    
    try:
        trans = tfBuffer.lookup_transform('base_link', 'target_object', rospy.Time())
    except (tf2_ros.LookupException, tf2_ros.ConnectivityException, tf2_ros.ExtrapolationException):
        rate.sleep()

    if result:
        # Checking the MoveItErrorCode
        if result.error_code.val == MoveItErrorCodes.SUCCESS:
            rospy.loginfo("Disco!")
        else:
            # If you get to this point please search for:
            # moveit_msgs/MoveItErrorCodes.msg
            rospy.logerr("Arm goal in state: %s",
                         move_group.get_move_action().get_state())
    else:
        rospy.logerr("MoveIt! failure no result returned.")
    
    move_group.get_move_action().cancel_all_goals()

def halt():
    global msg, pub 
    rate = rospy.Rate(50)
    msg.linear.x = 0.0
    msg.angular.z = 0.0
    pub.publish(msg)
    rospy.loginfo("Stopping")
    rate.sleep()

def findCube():
    global foundCube, msg, pub, rate
    
    rospy.Subscriber('/contour_red/moments', MomentArrayStamped, findRed)
 #   if foundCube:
    while not foundCube:
        rospy.loginfo("Spinning for cube")
        msg.linear.x = 0.0
        msg.angular.z = 2.0        
        pub.publish(msg)
        # Send a message to rosout with the details
        # Wait until it's time for another iteration
        rate.sleep()
    msg.linear.x = 0.0
    msg.angular.y = 0.0
    pub.publish(msg)
    halt()

def moveToCube():
    global pub,x,y,areaC,areaTHC, msg, rate #y < 400 before lowering head.
    while areaC <= areaTHC:
        if x > 0:
            msg.linear.x=1.0
            msg.angular.z= -0.3
            pub.publish(msg)
            rate.sleep()
        rospy.loginfo("Moving")
        msg.linear.x = 1.0
        msg.angular.z = 0.0
        pub.publish(msg) 
        rate.sleep()
    msg.linear.x = 0.0
    msg.angular.y = 0.0
    pub.publish(msg)
    rospy.loginfo("Freedom")
    halt() # also tilt head

def findBin():
    global foundBin, msg, pub, rate
    
    rospy.Subscriber('/contour_green/moments', MomentArrayStamped, findGreen)
    #   if foundCube:
    while not foundBin:
        rospy.loginfo("Spinning for Bin")
        msg.linear.x = 0.0
        msg.angular.z = 2.0        
        pub.publish(msg)
        # Send a message to rosout with the details
        # Wait until it's time for another iteration
        rate.sleep()
    msg.linear.x = 0.0
    msg.angular.y = 0.0
    pub.publish(msg)
    halt()

def moveToBin():
    global pub,x,y,areaB,areaTHB, msg, rate #y < 400 before lowering head.
    while areaB <= areaTHB:
        if y < 400:
            readyHead()
        if x > 0:
            msg.linear.x=1.0
            msg.angular.z= 0.2
            pub.publish(msg)
            rate.sleep()
        rospy.loginfo("Moving")
        msg.linear.x = 1.0
        msg.angular.z = 0.0
        pub.publish(msg) 
        rate.sleep()
    msg.linear.x = 0.0
    msg.angular.y = 0.0
    pub.publish(msg)
    rospy.loginfo("Freedom")
    halt() # also tilt head
    
    
def findGreen(msg):
    global foundBin, x, y, areaB
    momentsList = msg.moments
    if  len(momentsList) > 0:
        rospy.loginfo("position=(%.2f,%.2f) area=%.2f bin",\
        momentsList[0].center.x,\
        momentsList[0].center.y,\
        momentsList[0].area)
        foundBin = True
        x=momentsList[0].center.x
        y=momentsList[0].center.y
        area=momentsList[0].area

def findRed(msg):
    global foundCube, x, y, areaC
    momentsList = msg.moments
    if  len(momentsList) > 0:
        rospy.loginfo("position=(%.2f,%.2f) area=%.2f cube",\
        momentsList[0].center.x,\
        momentsList[0].center.y,\
        momentsList[0].area)
        foundCube = True
        x=momentsList[0].center.x
        y=momentsList[0].center.y
        area=momentsList[0].area

if __name__ == '__main__':
    rospy.init_node('fetch_find')
    
    rospy.Subscriber('/head_camera/depth_registered/image_raw', Image, depthPerception)
     
    globalVariables()
    
    readyUpBody()
    #findCube()
    #moveToCube()   
    #readyHead() # after moving to object
    #halt()
    #pickUp()
    resetHead()
    #readyUpBody()
        
    #findBin()
    #moveToBin()
    #pickUp()
    
    rospy.loginfo("Hello There")
