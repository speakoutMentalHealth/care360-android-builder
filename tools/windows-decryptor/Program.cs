using System;
using System.Collections.Generic;
using System.Formats.Tar;
using System.IO;
using System.IO.Compression;
using System.Linq;
using System.Security.Cryptography;
using System.Text;

internal static class Program
{
    private static readonly byte[] Magic = Encoding.ASCII.GetBytes("K3E1");
    private static readonly byte[] AAD = Encoding.UTF8.GetBytes("Care360 synthetic Android debug artifact v1");
    private static readonly HashSet<string> AllowedNames = new(StringComparer.Ordinal)
    {
        "BUILD-INFO.txt",
        "build-log.txt",
        "Care360-Patient-OFFLINE-debug.apk",
        "Care360-Patient-LAN-debug.apk",
        "Care360-Patient-STAGING-debug.apk"
    };

    public static int Main(string[] args)
    {
        Console.WriteLine("Care360 Patient encrypted APK decryptor");
        Console.WriteLine("Works without Python, Flutter or Android Studio.");
        Console.WriteLine();

        try
        {
            string file;
            if (args.Length > 0 && args[0] != "--password-env")
            {
                file = Path.GetFullPath(args[0]);
            }
            else
            {
                var candidates = Directory.GetFiles(Environment.CurrentDirectory, "*.k3enc");
                if (candidates.Length != 1)
                {
                    Console.Error.WriteLine("Put this program beside exactly one .k3enc file, or drag the file onto this program.");
                    return 2;
                }
                file = Path.GetFullPath(candidates[0]);
            }

            if (!File.Exists(file))
            {
                Console.Error.WriteLine("Encrypted file not found: " + file);
                return 2;
            }
            if (new FileInfo(file).Length > 1024L * 1024 * 1024)
            {
                Console.Error.WriteLine("Encrypted file is unusually large (>1 GB); refusing to allocate memory.");
                return 2;
            }
            string password = ReadPassword(args);
            if (password.Length < 32)
            {
                Console.Error.WriteLine("The configured password must contain at least 32 characters.");
                return 2;
            }

            Console.WriteLine("Authenticating and decrypting the file...");
            byte[] encrypted = File.ReadAllBytes(file);
            if (encrypted.Length < 49 || !encrypted.AsSpan(0, 4).SequenceEqual(Magic))
            {
                Console.Error.WriteLine("Not a recognized Care360 .k3enc artifact.");
                return 2;
            }
            byte[] salt = encrypted.AsSpan(4, 16).ToArray();
            byte[] nonce = encrypted.AsSpan(20, 12).ToArray();
            int cipherLength = encrypted.Length - 32 - 16;
            byte[] clear = new byte[cipherLength];
            byte[] key = Rfc2898DeriveBytes.Pbkdf2(
                Encoding.UTF8.GetBytes(password), salt, 600_000, HashAlgorithmName.SHA256, 32);
            try
            {
                using var aes = new AesGcm(key, 16);
                aes.Decrypt(
                    nonce,
                    encrypted.AsSpan(32, cipherLength),
                    encrypted.AsSpan(encrypted.Length - 16, 16),
                    clear,
                    AAD
                );
            }
            catch (CryptographicException)
            {
                Console.Error.WriteLine("Decryption failed: incorrect password or damaged encrypted download.");
                return 1;
            }
            finally
            {
                CryptographicOperations.ZeroMemory(key);
            }

            try
            {
                string directory = Path.Combine(Path.GetDirectoryName(file)!, "Care360-Decrypted");
                Directory.CreateDirectory(directory);
                var extracted = new List<string>();
                using var raw = new MemoryStream(clear, writable: false);
                using var gzip = new GZipStream(raw, CompressionMode.Decompress);
                using var tar = new TarReader(gzip);
                TarEntry? entry;
                while ((entry = tar.GetNextEntry()) != null)
                {
                    if (entry.EntryType != TarEntryType.RegularFile &&
                        entry.EntryType != TarEntryType.V7RegularFile)
                        continue;

                    string name = entry.Name;
                    while (name.StartsWith("./", StringComparison.Ordinal))
                        name = name.Substring(2);

                    // Allow a fixed set of files only; prevent path traversal.
                    if (!AllowedNames.Contains(name))
                        continue;

                    string destination = Path.Combine(directory, name);
                    if (File.Exists(destination))
                    {
                        Console.Error.WriteLine("Refusing to overwrite an existing output file: " + destination);
                        return 2;
                    }
                    using var output = File.Create(destination);
                    entry.DataStream?.CopyTo(output);
                    extracted.Add(name);
                }

                if (extracted.Count == 0)
                {
                    Console.Error.WriteLine("Archive opened, but no recognized Care360 files were found.");
                    return 1;
                }
                Console.WriteLine();
                Console.WriteLine("SUCCESS. Extracted to: " + directory);
                foreach (string name in extracted)
                    Console.WriteLine(" - " + name);
                if (extracted.Any(name => name.EndsWith("-debug.apk", StringComparison.Ordinal)))
                    Console.WriteLine("APK extracted. Check BUILD-INFO.txt before installing: offline, staging and LAN builds have different restrictions.");
                else
                    Console.WriteLine("This artifact contains diagnostics but no compiled APK.");
                return 0;
            }
            finally
            {
                CryptographicOperations.ZeroMemory(clear);
            }
        }
        catch (Exception ex) when (ex is IOException or UnauthorizedAccessException or InvalidDataException or ArgumentException or CryptographicException)
        {
            Console.Error.WriteLine("Unable to open/decrypt the artifact: " + ex.Message);
            return 1;
        }
        finally
        {
            if (!Console.IsInputRedirected)
            {
                Console.WriteLine();
                Console.WriteLine("Press Enter to close.");
                Console.ReadLine();
            }
        }
    }

    private static string ReadPassword(string[] args)
    {
        int index = Array.IndexOf(args, "--password-env");
        if (index >= 0)
        {
            if (index + 1 >= args.Length)
                throw new ArgumentException("--password-env requires an environment variable name.");
            return Environment.GetEnvironmentVariable(args[index + 1]) ?? "";
        }

        if (Console.IsInputRedirected)
            throw new ArgumentException("Interactive password input required; open this program in a terminal.");

        Console.Write("Enter the saved K3_BUILD_OUTPUT_PASSWORD (hidden): ");
        var password = new StringBuilder();
        while (true)
        {
            var key = Console.ReadKey(intercept: true);
            if (key.Key == ConsoleKey.Enter)
                break;
            if (key.Key == ConsoleKey.Backspace)
            {
                if (password.Length > 0)
                    password.Length -= 1;
                continue;
            }
            if (!char.IsControl(key.KeyChar))
                password.Append(key.KeyChar);
        }
        Console.WriteLine();
        return password.ToString();
    }
}
