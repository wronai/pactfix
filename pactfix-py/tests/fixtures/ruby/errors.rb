# Ruby Error Fixture - 14 different error types

class ErrorExamples
  # RUBY001: Using == instead of .nil?
  def check_value(val)
    if val == nil
      puts "Value is nil"
    end
  end
  
  # RUBY002: Using rescue without exception class
  def risky_operation
    begin
      do_something_dangerous
    rescue
      puts "Error occurred"
    end
  end
  
  # RUBY003: Rescuing Exception (catches everything)
  def another_risky_operation
    begin
      process_data
    rescue Exception => e
      puts e.message
    end
  end
  
  # RUBY004: Using puts/print for logging
  def process
    puts "Starting process..."
    print "Progress: "
  end
  
  # RUBY005: Hardcoded credentials
  PASSWORD = "secret123"
  API_KEY = "sk-abcdef123456"
  TOKEN = "bearer-token-xyz"
  
  # RUBY006: Using eval
  def dynamic_call(code)
    eval(code)
    result = eval("1 + 2")
  end
  
  # RUBY007: Using send with user input
  def call_method(method_name, obj)
    obj.send(method_name)
  end
  
  # RUBY008: SQL injection risk
  def find_user(id)
    User.where("id = #{id}")
    User.find_by_sql("SELECT * FROM users WHERE id = #{id}")
  end
  
  # RUBY009: Using class variables @@
  @@counter = 0
  @@cache = {}
  
  def increment
    @@counter += 1
  end
  
  # RUBY010: Not using freeze for constants
  DEFAULT_NAME = "Unknown"
  CONFIG_PATH = "/etc/app/config"
  
  # RUBY011: Using return in proc
  def process_with_proc
    my_proc = proc do |x|
      return x * 2 if x > 10
      x
    end
    my_proc.call(15)
  end
  
  # RUBY012: Method too long (simulated)
  def very_long_method
    # line 1
    # line 2
    # line 3
    # line 4
    # line 5
    # line 6
    # line 7
    # line 8
    # line 9
    # line 10
    # line 11
    # line 12
    # line 13
    # line 14
    # line 15
    # line 16
    # line 17
    # line 18
    # line 19
    # line 20
    # line 21
  end
  
  # RUBY013: Using begin/rescue for control flow
  def check_existence(key)
    begin
      data[key]
    rescue KeyError
      nil
    end
  end
  
  # RUBY014: Double negation
  def is_present?(value)
    !!value
  end
end
