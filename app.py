from flask import Flask , render_template
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from  flask_sqlalchemy import SQLAlchemy 
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField,IntegerField,SelectField, SelectMultipleField, FieldList,FormField
from wtforms.validators import Length
from wtforms.validators import DataRequired
from flask_admin.form import ImageUploadField
from flask_wtf.file import FileAllowed
from Utilities import Utils
import datetime 
import os
import hidden
from wtforms_sqlalchemy.fields import QuerySelectField

import markdown

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SECRET_KEY'] = hidden.password
db = SQLAlchemy(app)


# Classes for Static fixed files images
class BannerImages(db.Model):
    __tablename__ = 'Banner Image'
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(255), nullable=True)

class BannerImagesForm(FlaskForm):
    banner_image = ImageUploadField('Banner Image',base_path='static/fixed/', validators=[DataRequired(message='This field cannot be empty')])

class BannerImageView(ModelView):
    form = BannerImagesForm

    column_list = ['id', 'image']

    column_searchable_list = ['id']

    column_filters = ['id']

    create_modal = True
    edit_modal = True

    form_widget_args = {
        'id': {
            'rows': 5
        },
        'image': {
            'rows': 5
        }
    }

    form_extra_fields = {
        'image': ImageUploadField('Banner Image', thumbnail_size=(100, 100, True), validators=[DataRequired()])
    }

# Article table

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    main_image = db.Column(db.String(255), nullable=True)
    epigraph = db.Column(db.Text, nullable=True)
    paragraphs = db.relationship('Paragraph', backref='article', cascade='all, delete-orphan')
    content_image = db.relationship('Image', backref = 'article', cascade = 'all, delete-orphan')
    

class Paragraph(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    image = db.relationship('Image', backref='paragraph', uselist=False)
    para_number = db.Column(db.Integer, nullable=False) 
    article_id = db.Column(db.Integer, db.ForeignKey('article.id', ondelete='CASCADE'),name='fk_paragraph_to_articles')

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content_image = db.Column(db.String(255),db.ForeignKey('article.id', ondelete='CASCADE') ,name = 'fk_content_image_to_articles')
    paragraph_id = db.Column(db.Integer, db.ForeignKey('paragraph.id', ondelete='CASCADE'),name = 'fk_image_paragraph')

    
    
class ParagraphForm(FlaskForm):
    article_id = QuerySelectField('Article', query_factory=lambda: Article.query.all(), allow_blank=False, get_label='id')
    text = TextAreaField('Text', validators=[DataRequired(), Length(min=10)])
    
    def populate_obj(self, obj):
        super().populate_obj(obj)
        selected_article = self.article_id.data
        if selected_article:
            obj.article_id = selected_article.id
            
            # Query the Paragraph table to find the maximum paragraph number for the given article_id
            max_paragraph_number = Paragraph.query.filter_by(article_id=selected_article.id).order_by(Paragraph.para_number.desc()).first()

            if max_paragraph_number:
                # If there are paragraphs for the given article, increment the maximum paragraph number by 1
                next_paragraph_number = max_paragraph_number.para_number + 1
            else:
                # If there are no paragraphs for the given article, set the paragraph number to 1
                next_paragraph_number = 1

            obj.para_number = next_paragraph_number
            
            
ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'webp'}



class ImageForm(FlaskForm):
    article_id = QuerySelectField('Article', query_factory=lambda: Article.query.all(), allow_blank=False, get_label='id')
    paragraph = QuerySelectField('Paragraph', allow_blank=False, get_label='para_number')
    image = ImageUploadField('Image', base_path='static/ArticleImage/ContentImage', thumbnail_size=(100, 50, True),
                             validators=[
                                 DataRequired(),
                                 FileAllowed(ALLOWED_IMAGE_EXTENSIONS, 'Images only!')
                             ])

    def __init__(self, *args, **kwargs):
        super(ImageForm, self).__init__(*args, **kwargs)
        self.paragraph.query_factory = self.get_paragraph_choices

    def get_paragraph_choices(self):
        selected_article_id = self.article_id.data.id if self.article_id.data else None
        if selected_article_id:
            return Paragraph.query.filter_by(article_id=selected_article_id).all()
        else:
            return []

        
        


class ArticleForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    epigraph = TextAreaField('Epigraph',validators=[Length(min=10,max=200)])
    main_image = ImageUploadField('Image', base_path='static/ArticleImage', thumbnail_size=(200, 100, True), validators=[DataRequired()])
   
    

    

class ParagraphView(ModelView):
    form = ParagraphForm
    column_list = ['id','para_number','article_id','text']
    form_widget_args = {
        'id': {
            'rows': 5
        },
        'article_id': {
            'rows': 10
        },
        'mainimage' : {
            'rows' : 20
        }
    }
    

class ImageView(ModelView):
    form = ImageForm
    form_columns = ['paragraph','image']


    
class ArticleView(ModelView):
    
    form = ArticleForm
    
    column_list = ['id','title', 'epigraph', 'main_image']

    column_searchable_list = ['title', 'epigraph']

    column_filters = ['title']

    # Model creation allowed
    
    create_modal = True
    
    
    edit_modal = True
    

    form_widget_args = {
        'title': {
            'rows': 10
        },
        'content': {
            'rows': 15
        },
        'mainimage' : {
            'rows' : 10
        }
    }


    
migrate = Migrate(app,db,render_as_batch=True)

# # set optional bootswatch theme
app.config['FLASK_ADMIN_SWATCH'] ='lumen'

admin = Admin(app, name='microblog', template_mode='bootstrap3')


admin.add_view(BannerImageView(BannerImages, db.session))

admin.add_view(ArticleView(Article, db.session))
admin.add_view(ParagraphView(Paragraph, db.session))
admin.add_view(ImageView(Image, db.session)) 



# Routing begins
@app.route('/')
def homepage():
    return render_template('home.html')

@app.route('/articles')
def home():
    articles = Article.query.all()
    return render_template('articles.html', articles= articles)

@app.route('/article/<article_id>')
def article(article_id):
    article = Article.query.get(article_id)
    images = Image.query.join(Paragraph).filter(Paragraph.article_id == article_id).all()
    # print(images[0])
    # print(images.content_image)
    print('xxxxXxxxxxxxxxxxXXXXXXXXXXXXX')
    return render_template('article.html', article=article, images=images)




# Setting environment methods
app.jinja_env.filters['date_format'] =  Utils.datetime_format


if __name__ == '__main__':
    app.run(debug=True)