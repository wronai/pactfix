FROM ruby:3.3-slim
WORKDIR /app
COPY Gemfile* ./
RUN bundle install 2>/dev/null || true
COPY . .
CMD ["bundle", "exec", "rspec", "||", "ruby", "main.rb"]
