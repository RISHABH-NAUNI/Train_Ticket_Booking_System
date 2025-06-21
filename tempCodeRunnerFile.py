@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        uname = request.form['username']
        pwd = request.form['password']
        is_vip = 'is_vip' in request.form

        #  Strong password enforcement
        if not is_strong_password(pwd):
            flash('Password must be at least 8 characters long, contain one uppercase letter, one lowercase letter, one number, and one special character.')
            return redirect(url_for('register'))

        if User.query.filter_by(username=uname).first():
            flash('Username already exists.')
            return redirect(url_for('register'))

        hashed_pwd = generate_password_hash(pwd)
        new_user = User(username=uname, password=hashed_pwd, is_vip=is_vip)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')