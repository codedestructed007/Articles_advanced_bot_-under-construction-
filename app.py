from flask import Flask , render_template
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from  flask_sqlalchemy import SQLAlchemy 
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField,IntegerField, SelectMultipleField, FieldList,FormField
from wtforms.validators import Length
from wtforms.validators import DataRequired
from flask_admin.form import ImageUploadField
from flask_wtf.file import FileAllowed
from Utilities import Utils
import datetime 
import os
import hidden


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

class Paragraph(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order = db.Column(db.Integer, nullable=False, unique=True)
    text = db.Column(db.Text, nullable=False)
    image = db.relationship('Image', backref='paragraph', uselist=False)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id', ondelete='CASCADE'))

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content_image = db.Column(db.String(255), nullable=True)
    paragraph_id = db.Column(db.Integer, db.ForeignKey('paragraph.id', ondelete='CASCADE'))
    
class ParagraphForm(FlaskForm):
    order = StringField('Order', validators=[DataRequired()])
    text = TextAreaField('Text', validators=[DataRequired(), Length(min=10)])

ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'webp'}
class ImageForm(FlaskForm):
    caption = StringField('Caption')
    image = ImageUploadField('Image', base_path='static/ArticleImage/ContentImage', thumbnail_size=(100,50, True),
        validators=[
            DataRequired(), 
            FileAllowed(ALLOWED_IMAGE_EXTENSIONS, 'Images only!'),]
        )
    # Add more fields as needed

class ArticleForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    epigraph = TextAreaField('Epigraph',validators=[Length(min=10,max=200)])
    main_image = ImageUploadField('Image', base_path='static/ArticleImage', thumbnail_size=(200, 100, True), validators=[DataRequired()])
   
    
    # def __init__(self, *args, **kwargs):
    #     super(ArticleForm, self).__init__(*args, **kwargs)
    #     self.paragraphs.choices = [(paragraph.id, paragraph.text) for paragraph in Paragraph.query.all()]



# class ImageForm(FlaskForm):
#     content_image = ImageUploadField('Content image', base_path='static/ArticleImage/ContentImage', thumbnail_size=(200,100, True))
    
    

class ParagraphView(ModelView):
    form_columns = ['article_id' ,'order','text', 'image']
    column_auto_select_related=True
    

class ImageView(ModelView):
    form = ImageForm
    form_columns = ['content_image']


    
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
#     inline_models = [
#         (Paragraph, {
#             'form_label' : 'Paragraph',
#             'form_columns' : {
#                 'order' : IntegerField('Paragraph position'),
#                 'text' : TextAreaField('Content')
#             }
#         }),
#         (Image, {
#             'form_label' : 'Images',
#             'form_columns' : {
#                 'content_image' : ImageUploadField('Paragraph respective image')
#             }
# #         })
    # ]
    
    


    
migrate = Migrate(app,db)

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
    return render_template('article.html', article=article, images=images)




# Setting environment methods
app.jinja_env.filters['date_format'] =  Utils.datetime_format


if __name__ == '__main__':
    app.run(debug=True)