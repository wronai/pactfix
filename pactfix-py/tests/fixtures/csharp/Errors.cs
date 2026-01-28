// C# Error Fixture - 17 different error types
using System;
using System.Data.SqlClient;
using System.IO;
using System.Threading;
using System.Threading.Tasks;

namespace ErrorFixtures
{
    public class Errors
    {
        // CS001: Using == for string comparison
        public bool CheckName(string name)
        {
            return name == "admin";
        }
        
        // CS002: Catching generic Exception
        public void ReadFile()
        {
            try
            {
                File.ReadAllText("test.txt");
            }
            catch (Exception ex)
            {
                // too broad
            }
        }
        
        // CS003: Empty catch block
        public void ProcessData()
        {
            try
            {
                int x = 1 / 0;
            }
            catch (DivideByZeroException)
            {
            }
        }
        
        // CS004: Using Console.WriteLine for logging
        public void DoWork()
        {
            Console.WriteLine("Starting work...");
            Console.Write("Progress: ");
        }
        
        // CS005: Hardcoded credentials
        private string password = "secret123";
        private string connectionString = "Server=localhost;Password=admin123";
        
        // CS006: Using var for unclear types
        public void ProcessItems()
        {
            var result = service.GetData();
            var items = processor.Process();
        }
        
        // CS007: Public fields instead of properties
        public string Username;
        public int Age;
        
        // CS008: async void methods
        public async void LoadDataAsync()
        {
            await Task.Delay(1000);
        }
        
        // CS009: Not awaiting async call
        public void StartProcess()
        {
            LoadDataAsync();
            ProcessAsync();
        }
        
        // CS010: Using lock(this)
        public void UpdateCounter()
        {
            lock(this)
            {
                // dangerous
            }
        }
        
        // CS011: Using string concatenation instead of interpolation
        public string FormatMessage(string name, int age)
        {
            return "Name: " + name + ", Age: " + age;
        }
        
        // CS012: Not disposing IDisposable
        public void ReadStream()
        {
            var stream = new FileStream("data.txt", FileMode.Open);
            var reader = new StreamReader(stream);
            string content = reader.ReadToEnd();
        }
        
        // CS013: SQL injection risk
        public void GetUser(SqlConnection conn, string id)
        {
            var cmd = new SqlCommand("SELECT * FROM Users WHERE Id = " + id, conn);
            cmd.ExecuteReader();
        }
        
        // CS014: Using Thread.Sleep
        public void WaitAndContinue()
        {
            Thread.Sleep(5000);
        }
        
        // CS016: Using DateTime.Now instead of DateTimeOffset
        public void LogTime()
        {
            var now = DateTime.Now;
            var today = DateTime.Today;
        }
        
        // CS017: Magic numbers
        public bool IsValid(int value)
        {
            return value > 100 && value < 9999;
        }
    }
}
