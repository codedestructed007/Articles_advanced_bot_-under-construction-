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
from flask_bootstrap import Bootstrap
import hidden
from wtforms_sqlalchemy.fields import QuerySelectField
import markdown
from flask_babel import Babel

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SECRET_KEY'] = hidden.password
db = SQLAlchemy(app)
babel = Babel(app)
bootstrap = Bootstrap(app)

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




class ArticleForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    epigraph = TextAreaField('Epigraph',validators=[Length(min=10,max=200)])
    main_image = ImageUploadField('Image', base_path='static/ArticleImage', thumbnail_size=(200, 100, True), validators=[DataRequired()])
   
# Image wtf form
class Imageform(FlaskForm):
    paragraph_id = QuerySelectField(
        'Paragraph',
        query_factory=lambda: Paragraph.query.all(),
        get_label='id',
        validators=[DataRequired()]
    )
    image = ImageUploadField('Image', base_path='static/ArticleImage/ContentImage',validators=[DataRequired()])

    def populate_obj(self, obj):
        super().populate_obj(obj)
        selected_paragraph = self.paragraph_id.data
        if selected_paragraph:
            obj.paragraph_id = selected_paragraph.id
            obj.content_image = self.image.data.filename

class ImageView(ModelView):
    form = Imageform
    column_list = ['id', 'paragraph_id', 'content_image']
    form_extra_fields = {
        'content_image': ImageUploadField('Image', thumbnail_size=(100, 100, True), validators=[DataRequired()])
    }
    

class ParagraphView(ModelView):
    form = ParagraphForm
    column_list = ['id', 'para_number', 'article_title', 'text']  # Include 'article_title' in column list

    def get_query(self):
        return super(ParagraphView, self).get_query().join(Article)  # Join with Article model

    def get_list(self, page, sort_column, sort_desc, search, filters, execute=True, page_size=None):
        self.column_labels = {'article_title': 'Article Title'}  # Set custom label for article_title column
        return super(ParagraphView, self).get_list(page, sort_column, sort_desc, search, filters, execute, page_size)

    def scaffold_list_columns(self):
        columns = super(ParagraphView, self).scaffold_list_columns()
        columns['article_title'] = self._get_column_by_attr('article', 'title')  # Add article_title column
        return columns
    
    
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
    article = Article.query.get_or_404(article_id)
    return render_template('article.html', article=article)

@app.route('/temp')
def temp():
    return render_template('temp.html')


# Setting environment methods
app.jinja_env.filters['date_format'] =  Utils.time_ago


if __name__ == '__main__':
    app.run(debug=True)