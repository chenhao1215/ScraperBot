import urllib2
import xmlrpclib
import time
import datetime
import dataHandler
import random
from random import randint
import calendar
from wordpress_xmlrpc.base import Client
from wordpress_xmlrpc.methods.posts import GetRecentPosts, NewPost
from wordpress_xmlrpc.wordpress import WordPressPost

class PostCreator():

    def __init__( self ):
        #=======================================================================
        # self.wp_site = "http://localhost/wordpress/xmlrpc.php"
        # self.url = "http://localhost/wordpress/xmlrpc.php"
        #=======================================================================
        self.wp_site = "http://www.hottestporn4u.com/xmlrpc.php"
        self.url = "http://www.hottestporn4u.com/xmlrpc.php"
        self.login = "pornmaster"
        self.password = "pornmasterpiece"
        self.wp = Client( self.wp_site, self.login, self.password )
        self._server = xmlrpclib.ServerProxy( self.url )
        #self._server = xmlrpclib.Server(self.url)
        self.blogId = 0
        self.dataHandler = dataHandler.DataHandler()
        self.categoriesList = self.dataHandler.read_categories()
        self.getCategoryList = self.getCategoriesFromBlog()

    def get_url_content( self, url ):
        try:
            content = urllib2.urlopen( url )
            return content.read()
        except:
            print 'error! NOOOOOO!!!'

    def enter_WP_user( self ):
        user = raw_input ( "WP user >> " )
        return user

    def enter_WP_password( self ):
        password = raw_input ( "WP password >> " )
        return password

    def uploadFileToWp( self, thumbnail ):
        print "Client connected ..."
        # set to the path to your file
        file_url = thumbnail
        extension = file_url.split( "." )
        leng = extension.__len__()
        extension = extension[leng - 1]
        if ( extension == 'jpg' ):
            xfileType = 'image/jpeg'
        elif( extension == 'png' ):
            xfileType = 'image/png'
        elif( extension == 'bmp' ):
            xfileType = 'image/bmp'

        file = self.get_url_content( file_url )
        file = xmlrpclib.Binary( file )
        server = xmlrpclib.Server( self.wp_site )
        filename = str( time.strftime( '%H:%M:%S' ) )
        mediarray = {'name':filename + '.' + extension,
                     'type':xfileType,
                     'bits':file,
                     'overwrite':'false'}
        xarr = ['1', self.login, self.password, mediarray]
        result = server.wp.uploadFile( xarr )
        print result

    def createPost( self, title, thumbnail, iframe, videoduration, snippets_Duration, categories, url ):
        print "WP creating post ..."
        average = str( round( self.prepare_rating_for_post(), 2 ) )
        number_of_votes = str( self.prepare_number_of_votes() )
        dateFormat = self.prepare_post_date()
        post = WordPressPost()
        post.title = title
        post.description = '<div class="hreview-aggregate"><div class="item vcard"><div itemscope itemtype="http://schema.org/VideoObject"><h2 class="fn"><meta itemprop="embedURL" content="' + url + '" />' + iframe + '<p><span itemprop="name">' + title + '</span></h2><meta itemprop="duration" content="' + snippets_Duration + '" /><h3>(' + videoduration + ')</h3><meta itemprop="thumbnailUrl" content="' + thumbnail + '" /><p><span itemprop="description">This video is called ' + title + '</span></div></div><span class="rating"><span class="average">' + average + '</span> out of <span class="best"> 10 </span>based on <span class="votes">' + number_of_votes + ' </span>votes</span><p><img src="' + thumbnail + '" alt="' + title + '"><br></div>'
        post.categories = str( self.dataHandler.prepare_categories_for_post( categories, self.categoriesList ) )
        post.tags = str( self.dataHandler.prepare_tags_for_post( title ) )
        post.date = str( dateFormat )

        print "post.title " + post.title
        print "post.description " + post.description
        print "post.categories " + post.categories
        print "post.tags " + post.tags
        print "post.date_created " + post.date

        #prepare categories
        cats = post.categories
        cats2 = cats.replace( "'", "" )
        cats3 = cats2.replace( "[", "" )
        cats4 = cats3.replace( "]", "" )
        cats5 = cats4.split( "," )
        catAux = []
        for cat1 in cats5:
            catAux.append( cat1.strip() )

        post.categories = catAux
        postId = self.wp.call( NewPost( post, True ) )
        print "WP " + postId + " uploaded [OK]"
        return 0

    def prepare_rating_for_post( self ):
        var = random.uniform( 7.5, 10 )
        return var

    def prepare_number_of_votes( self ):
        var = random.randrange( 0, 10100, 2 )
        return var

    def prepare_post_date( self ):
        now = datetime.datetime.now()
        lastDay = self.get_last_day_of_the_month( now )
        if now.day == lastDay.day:
            day = randint( 1, lastDay.day )
            month = now.month + 1
        elif ( calendar.isleap( now.year ) and now.day == 29 ):
            day = randint( 1, lastDay.day )
            month = now.month + 1
        elif ( not( calendar.isleap( now.year ) ) and now.day == 28 ):
            day = randint( 1, lastDay.day )
            month = now.month + 1
        else:
            dayRange = now.day + 1
            day = randint( now.day, dayRange )
            month = now.month

        minute = randint( now.minute, 59 )
        hour = randint( 0, 23 )

        if month < 10:
            month = "0" + str( month )
        else:
            month = str( month )

        if day < 10:
            day = "0" + str( day )
        else:
            day = str( day )

        if hour < 10:
            hour = "0" + str( hour )
        else:
            hour = str( hour )

        if minute < 10:
            minute = "0" + str( minute )
        else:
            minute = str( minute )

        if now.second < 10:
            second = "0" + str( now.second )
        else:
            second = str( now.second )

        date = str( now.year ) + "" + month + "" + day + "T" + hour + ":" + minute + ":" + second
        return str( date )

    def get_posts( self, number_of_posts ):
        posts = self.wp.call( GetRecentPosts( 10 ) )
        return posts

    def get_last_day_of_the_month( self, date ):
        if date.month == 12:
            return date.replace( day = 31 )
        return date.replace( month = date.month + 1, day = 1 ) - datetime.timedelta( days = 1 )

    def getCategoryList( self ):
        """Get blog's categories list
        """

        try:
            if not self.categories:
                self.categories = []
                categories = self._server.mt.getCategoryList( self.blogId,
                                                self.login, self.password )
                for cat in categories:
                    self.categories.append( self._filterCategory( cat ) )

            return self.categories
        except xmlrpclib.Fault, fault:
            print "Error:  Wordpress exception!"

    def getCategoriesFromBlog( self ):
        """Get categories from Wordpress blog
        """
        categoriesStruct = self._server.metaWeblog.getCategories( self.blogId, self.login, self.password )
        return categoriesStruct

    def getCategoryIdFromName( self, name ):
        """Get category id from category name
        """
        for c in self.getCategoryList:
            if c['categoryName'] == name:
                return c['categoryId']
