import inspect
import logging

from flask import jsonify
from google.appengine.ext import ndb

from ewentts.models import Post, User
from ewentts.utils import request_uid, error_decorator, BadRequestError

logger = logging.getLogger("posts")


def create_post(body, posts_num):
    """Create post of class Post

    Properties:
        body: json object containing information under keyword content
        posts_num: total number of posts

    Returns:
        post of Class Post

    Raises:
        BadRequestError if content not received
    """
    post_id = str(posts_num+1)
    creator_id = request_uid()
    creator_key = ndb.Key(User, creator_id)
    content = body.get("content")
    if not content:
        raise BadRequestError("Content of the post not received")
    post = Post(id=post_id,
                creator=creator_key,
                content=content)
    post.put()
    logger.info("post {} created".format(post.key.id()))
    return post


def jsonify_post(post, event):
    """Return properties of post in json

    Properties:
        event: object of class Event
        post: post which is to be viewed

    Returns:
        Properties of post in json:
            id: id of the post
            creator: key of the creator
            content of the post
    """
    creator = post.creator.get()
    event.posts += [post.put()]
    event.put()
    json = jsonify(post_id=post.key.id(),
                   creator=" ".join(creator.user_names),
                   post_datetime=post.post_datetime,
                   content=post.content)
    return json
