from flask_wtf import FlaskForm
from wtforms import DateField, FloatField, PasswordField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange


class RegisterForm(FlaskForm):
    full_name = StringField("Nome completo", validators=[DataRequired(), Length(max=120)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm = PasswordField("Conferma", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Registrati")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Accedi")


class PlantForm(FlaskForm):
    name = StringField("Nome impianto", validators=[DataRequired()])
    plant_type = SelectField("Tipologia", choices=[("fotovoltaico", "Fotovoltaico"), ("eolico", "Eolico"), ("cogenerazione", "Cogenerazione")])
    installed_kw = FloatField("kW installati", validators=[DataRequired(), NumberRange(min=0.1)])
    install_date = DateField("Data installazione", validators=[DataRequired()])
    submit = SubmitField("Salva")


class VehicleForm(FlaskForm):
    model = StringField("Modello", validators=[DataRequired()])
    battery_kwh = FloatField("Capacità batteria kWh", validators=[DataRequired(), NumberRange(min=0.1)])
    submit = SubmitField("Salva")


class MeasurementForm(FlaskForm):
    day = DateField("Giorno", validators=[DataRequired()])
    production_kwh = FloatField("Produzione kWh", validators=[DataRequired(), NumberRange(min=0)])
    consumption_kwh = FloatField("Consumo kWh", validators=[DataRequired(), NumberRange(min=0)])
    km_travelled = FloatField("Km percorsi", validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField("Registra")
